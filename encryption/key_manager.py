
import os

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

# Encryption configuration
KEY_LENGTH = 32
SALT_LENGTH = 16
NONCE_LENGTH = 12

# Fixed Scrypt parameters for version 1
SCRYPT_N = 2**15
SCRYPT_R = 8
SCRYPT_P = 1

MAX_PASSWORD_LENGTH = 1024


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(SALT_LENGTH)


def generate_nonce() -> bytes:
    """Generate a cryptographically secure random GCM nonce."""
    return os.urandom(NONCE_LENGTH)


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a 256-bit encryption key from a password using Scrypt.

    The password and derived key must never be stored.
    """

    if not isinstance(password, str):
        raise ValueError("Password must be a string.")

    if not password:
        raise ValueError("Password cannot be empty.")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password is too long.")

    if not isinstance(salt, bytes):
        raise ValueError("Salt must be bytes.")

    if len(salt) != SALT_LENGTH:
        raise ValueError("Invalid salt length.")

    try:
        password_bytes = password.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("Password contains invalid characters.") from error

    kdf = Scrypt(
        salt=salt,
        length=KEY_LENGTH,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P
    )

    return kdf.derive(password_bytes)
