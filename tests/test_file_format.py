
import sys
import json
import struct
import unittest

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from encryption.file_format import (
    MAGIC,
    MAX_HEADER_SIZE,
    GCM_TAG_LENGTH,
    serialize_header,
    build_aad,
    parse_file
)


class TestFileFormat(unittest.TestCase):

    def setUp(self):
        self.header = {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "kdf": "scrypt",
            "kdf_params": {
                "n": 32768,
                "r": 8,
                "p": 1
            },
            "original_filename": "sample.txt",
            "original_size": 4,
            "salt": "AAAAAAAAAAAAAAAAAAAAAA==",
            "nonce": "AAAAAAAAAAAAAAAA"
        }

    def create_edv_data(self, header_bytes=None):
        if header_bytes is None:
            header_bytes = serialize_header(self.header)

        prefix = (
            MAGIC
            + struct.pack(">I", len(header_bytes))
            + header_bytes
        )

        fake_ciphertext = b"DATA" + (b"0" * GCM_TAG_LENGTH)

        return prefix + fake_ciphertext

    def test_header_serialization(self):
        result = serialize_header(self.header)
        self.assertIsInstance(result, bytes)
        self.assertLessEqual(len(result), MAX_HEADER_SIZE)

    def test_header_serialization_is_consistent(self):
        first = serialize_header(self.header)
        second = serialize_header(self.header)

        self.assertEqual(first, second)

    def test_aad_creation(self):
        header_bytes = serialize_header(self.header)
        aad = build_aad(header_bytes)

        self.assertTrue(aad.startswith(MAGIC))

    def test_valid_file_parsing(self):
        data = self.create_edv_data()

        header, ciphertext, aad = parse_file(data)

        self.assertEqual(header["version"], 1)
        self.assertTrue(ciphertext)
        self.assertTrue(aad.startswith(MAGIC))

    def test_invalid_magic_rejected(self):
        data = b"INVALID!" + self.create_edv_data()[len(MAGIC):]

        with self.assertRaises(ValueError):
            parse_file(data)

    def test_empty_header_rejected(self):
        data = MAGIC + struct.pack(">I", 0) + b"0" * 16

        with self.assertRaises(ValueError):
            parse_file(data)

    def test_oversized_header_rejected(self):
        data = (
            MAGIC
            + struct.pack(">I", MAX_HEADER_SIZE + 1)
            + b"0" * (MAX_HEADER_SIZE + 1)
            + b"0" * GCM_TAG_LENGTH
        )

        with self.assertRaises(ValueError):
            parse_file(data)

    def test_duplicate_json_keys_rejected(self):
        duplicate_header = (
            b'{"version":1,"version":1}'
        )

        data = self.create_edv_data(duplicate_header)

        with self.assertRaises(ValueError):
            parse_file(data)

    def test_non_standard_json_constant_rejected(self):
        invalid_header = b'{"version":NaN}'

        data = self.create_edv_data(invalid_header)

        with self.assertRaises(ValueError):
            parse_file(data)

    def test_incomplete_file_rejected(self):
        data = self.create_edv_data()

        with self.assertRaises(ValueError):
            parse_file(data[:15])

    def test_invalid_header_type_rejected(self):
        with self.assertRaises(ValueError):
            serialize_header("invalid")

    def test_invalid_aad_type_rejected(self):
        with self.assertRaises(ValueError):
            build_aad("invalid")


if __name__ == "__main__":
    unittest.main()
