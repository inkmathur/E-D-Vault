
import base64
import binascii
import os
import re

from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from encryption.key_manager import (
    derive_key,
    SALT_LENGTH,
    NONCE_LENGTH,
    SCRYPT_N,
    SCRYPT_R,
    SCRYPT_P
)

from encryption.file_format import (
    FORMAT_VERSION,
    parse_file
)

from encryption.encrypt import (
    MAX_FILE_SIZE,
    atomic_write
)


MAX_PASSWORD_LENGTH = 1024
MAX_HEADER_SIZE = 16 * 1024
GCM_TAG_LENGTH = 16

MAX_ENCRYPTED_FILE_SIZE = (
    MAX_FILE_SIZE + MAX_HEADER_SIZE + 128
)


def decode_base64(value, expected_length):
    """Decode and validate Base64 metadata."""

    if not isinstance(value, str):
        raise ValueError("Invalid encryption metadata.")

    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("Invalid encryption metadata.") from None

    if len(decoded) != expected_length:
        raise ValueError("Invalid encryption metadata.")

    # Reject non-canonical Base64 representations.
    if base64.b64encode(decoded).decode("ascii") != value:
        raise ValueError("Invalid encryption metadata.")

    return decoded


def validate_header(header):
    """Validate all metadata before deriving the encryption key."""

    if not isinstance(header, dict):
        raise ValueError("Invalid EDV file metadata.")

    if type(header.get("version")) is not int:
        raise ValueError("Unsupported EDV file version.")

    if header.get("version") != FORMAT_VERSION:
        raise ValueError("Unsupported EDV file version.")

    if header.get("algorithm") != "AES-256-GCM":
        raise ValueError("Unsupported encryption algorithm.")

    if header.get("kdf") != "scrypt":
        raise ValueError("Unsupported key derivation method.")

    params = header.get("kdf_params")

    if not isinstance(params, dict):
        raise ValueError("Invalid Scrypt parameters.")

    expected_params = {
        "n": SCRYPT_N,
        "r": SCRYPT_R,
        "p": SCRYPT_P
    }

    if (
        set(params.keys()) != set(expected_params.keys())
        or any(
            type(params[key]) is not int
            for key in expected_params
        )
        or params != expected_params
    ):
        raise ValueError("Invalid Scrypt parameters.")

    original_size = header.get("original_size")

    if (
        type(original_size) is not int
        or original_size < 0
        or original_size > MAX_FILE_SIZE
    ):
        raise ValueError("Invalid original file size.")

    filename = header.get("original_filename")

    if (
        not isinstance(filename, str)
        or not filename
        or filename in (".", "..")
        or len(filename) > 255
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
        or re.match(r"^[A-Za-z]:", filename)
    ):
        raise ValueError("Invalid original filename.")

    salt = decode_base64(
        header.get("salt"),
        SALT_LENGTH
    )

    nonce = decode_base64(
        header.get("nonce"),
        NONCE_LENGTH
    )

    return salt, nonce, original_size


def decrypt_file(input_path, password, output_path):
    """
    Decrypt an EDV file after authenticating its contents.

    Plaintext is written only after AES-GCM authentication succeeds.
    Existing destination files are not overwritten.
    """

    if input_path is None or output_path is None:
        raise ValueError("Input and output paths are required.")

    source = Path(input_path)
    destination = Path(output_path)

    if not source.is_file():
        raise FileNotFoundError("Encrypted file does not exist.")

    if not isinstance(password, str) or not password:
        raise ValueError("Decryption password cannot be empty.")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Decryption password is too long.")

    # Check file size before reading.
    if source.stat().st_size > MAX_ENCRYPTED_FILE_SIZE:
        raise ValueError("Encrypted file exceeds the allowed size.")

    # Prevent using the same resolved path for input and output.
    if source.resolve() == destination.resolve():
        raise ValueError(
            "Input and output paths must be different."
        )

    # Read at most the allowed size plus one byte.
    # This also protects against a file growing after the size check.
    with source.open("rb") as encrypted_file:
        encrypted_data = encrypted_file.read(
            MAX_ENCRYPTED_FILE_SIZE + 1
        )

    if len(encrypted_data) > MAX_ENCRYPTED_FILE_SIZE:
        raise ValueError("Encrypted file exceeds the allowed size.")

    # Parse the EDV file structure.
    header, ciphertext, aad = parse_file(encrypted_data)

    # Validate metadata before performing Scrypt.
    salt, nonce, original_size = validate_header(header)

    # AES-GCM ciphertext includes a 16-byte authentication tag.
    expected_ciphertext_length = (
        original_size + GCM_TAG_LENGTH
    )

    if len(ciphertext) != expected_ciphertext_length:
        raise ValueError("Encrypted file structure is invalid.")

    # Derive the encryption key.
    key = derive_key(password, salt)

    # Authenticate and decrypt the encrypted contents.
    try:
        plaintext = AESGCM(key).decrypt(
            nonce,
            ciphertext,
            aad
        )

    except InvalidTag:
        raise ValueError(
            "Decryption failed: incorrect password or file has been modified."
        ) from None

    # Verify the recovered file size.
    if len(plaintext) != original_size:
        raise ValueError(
            "Decrypted file integrity check failed."
        )

    # Save only after authentication and size verification.
    # atomic_write protects existing destination files.
    atomic_write(destination, plaintext)

    return str(destination)
