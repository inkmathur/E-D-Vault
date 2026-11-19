
import hashlib
import hmac
from pathlib import Path


def calculate_sha256(file_path, chunk_size=1024 * 1024):
    """
    Calculate the SHA-256 hash of a file.

    Reads the file in chunks to avoid loading the entire
    file into memory.

    Returns:
        str: 64-character hexadecimal SHA-256 hash.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            "The supplied path is not a regular file."
        )

    if chunk_size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero."
        )

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def verify_sha256(file_path, expected_hash):
    """
    Verify a file against its previously recorded SHA-256 hash.

    Returns:
        bool: True if the hash matches, otherwise False.
    """

    if not isinstance(expected_hash, str):
        return False

    expected_hash = expected_hash.strip().lower()

    if len(expected_hash) != 64:
        return False

    try:
        bytes.fromhex(expected_hash)
    except ValueError:
        return False

    actual_hash = calculate_sha256(file_path)

    return hmac.compare_digest(
        actual_hash,
        expected_hash
    )
