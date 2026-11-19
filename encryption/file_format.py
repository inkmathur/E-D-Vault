
import json
import struct

MAGIC = b"EDVAULT1"
FORMAT_VERSION = 1
MAX_HEADER_SIZE = 16 * 1024
GCM_TAG_LENGTH = 16


def _reject_duplicate_keys(pairs):
    """Reject JSON objects containing duplicate keys."""

    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON metadata keys are not allowed.")

        result[key] = value

    return result


def _reject_json_constant(value):
    """Reject non-standard JSON values such as NaN and Infinity."""

    raise ValueError("Invalid JSON metadata constant.")


def serialize_header(header: dict) -> bytes:
    """Convert metadata into a consistent JSON byte sequence."""

    if not isinstance(header, dict):
        raise ValueError("EDV metadata must be a dictionary.")

    try:
        header_bytes = json.dumps(
            header,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False
        ).encode("utf-8")

    except (TypeError, ValueError, UnicodeEncodeError):
        raise ValueError("Unable to serialize EDV metadata.") from None

    if not header_bytes or len(header_bytes) > MAX_HEADER_SIZE:
        raise ValueError("Invalid EDV header size.")

    return header_bytes


def build_aad(header_bytes: bytes) -> bytes:
    """
    Build Additional Authenticated Data.

    The header is authenticated by AES-GCM but is not encrypted.
    """

    if not isinstance(header_bytes, bytes):
        raise ValueError("Invalid EDV header data.")

    if not header_bytes or len(header_bytes) > MAX_HEADER_SIZE:
        raise ValueError("Invalid EDV header size.")

    length_bytes = struct.pack(">I", len(header_bytes))

    return MAGIC + length_bytes + header_bytes


def parse_file(data: bytes):
    """Read and validate the basic structure of an EDV file."""

    if not isinstance(data, bytes):
        raise ValueError("Invalid EDV file data.")

    prefix_size = len(MAGIC) + 4

    # Minimum structure: magic + length + at least one header byte + GCM tag.
    if len(data) < prefix_size + 1 + GCM_TAG_LENGTH:
        raise ValueError("Invalid or incomplete EDV file.")

    # Validate file signature.
    if data[:len(MAGIC)] != MAGIC:
        raise ValueError("Unrecognized EDV file format.")

    # Read header length.
    header_length = struct.unpack(
        ">I",
        data[len(MAGIC):prefix_size]
    )[0]

    if header_length == 0 or header_length > MAX_HEADER_SIZE:
        raise ValueError("Invalid EDV header length.")

    header_start = prefix_size
    header_end = header_start + header_length

    # Ensure enough bytes remain for the header and GCM tag.
    if header_end + GCM_TAG_LENGTH > len(data):
        raise ValueError("Incomplete EDV file.")

    header_bytes = data[header_start:header_end]

    # Decode JSON and reject ambiguous or non-standard metadata.
    try:
        header = json.loads(
            header_bytes.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant
        )

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
        RecursionError
    ):
        raise ValueError("Invalid EDV metadata.") from None

    if not isinstance(header, dict):
        raise ValueError("Invalid EDV metadata structure.")

    ciphertext = data[header_end:]

    # Reconstruct the exact authenticated header data.
    aad = build_aad(header_bytes)

    return header, ciphertext, aad
