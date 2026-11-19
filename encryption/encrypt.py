
import os
import base64
import struct
import tempfile

from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from encryption.key_manager import (
    generate_salt,
    generate_nonce,
    derive_key,
    SCRYPT_N,
    SCRYPT_R,
    SCRYPT_P
)

from encryption.file_format import (
    MAGIC,
    serialize_header,
    build_aad
)


MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_PASSWORD_LENGTH = 1024


def atomic_write(output_path: str, data: bytes):
    """
    Write data to a temporary file and create the destination
    without overwriting an existing file.
    """

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=".edvault-",
            suffix=".tmp",
            delete=False
        ) as temp_file:

            temp_path = Path(temp_file.name)
            temp_file.write(data)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        # Create the destination atomically.
        # Unlike os.replace(), os.link() will not overwrite
        # an existing destination.
        os.link(temp_path, destination)

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def encrypt_file(input_path, password, output_path=None):
    """Encrypt a file using Scrypt and AES-256-GCM."""

    source = Path(input_path)

    if not source.is_file():
        raise FileNotFoundError("Input file does not exist.")

    if not isinstance(password, str) or not password:
        raise ValueError("Encryption password cannot be empty.")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Encryption password is too long.")

    # Check file size before reading.
    if source.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 100 MB limit.")

    if output_path is None:
        destination = Path(str(source) + ".edv")
    else:
        destination = Path(output_path)

    # Prevent overwriting the original input file.
    if source.resolve() == destination.resolve():
        raise ValueError(
            "Input and output paths must be different."
        )

    # Read at most the permitted size plus one byte.
    # This also catches a file that grows after the size check.
    with source.open("rb") as source_file:
        original_data = source_file.read(MAX_FILE_SIZE + 1)

    if len(original_data) > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 100 MB limit.")

    # Generate fresh cryptographic values for this operation.
    salt = generate_salt()
    nonce = generate_nonce()
    key = derive_key(password, salt)

    # Create authenticated metadata.
    header = {
        "version": 1,
        "algorithm": "AES-256-GCM",
        "kdf": "scrypt",
        "kdf_params": {
            "n": SCRYPT_N,
            "r": SCRYPT_R,
            "p": SCRYPT_P
        },
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "original_filename": source.name,
        "original_size": len(original_data)
    }

    header_bytes = serialize_header(header)
    aad = build_aad(header_bytes)

    # Encrypt the file.
    aes = AESGCM(key)
    ciphertext = aes.encrypt(
        nonce,
        original_data,
        aad
    )

    # Build the complete EDV file.
    file_data = (
        MAGIC
        + struct.pack(">I", len(header_bytes))
        + header_bytes
        + ciphertext
    )

    # Save encrypted output without overwriting an existing file.
    atomic_write(destination, file_data)

    return str(destination)
