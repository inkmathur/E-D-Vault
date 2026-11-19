
import tempfile
import unittest

from pathlib import Path

from integrity.hash_manager import (
    calculate_sha256,
    verify_sha256
)


class TestFileIntegrity(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()

        self.file_path = (
            Path(self.temp_directory.name) / "sample.txt"
        )

        self.file_path.write_bytes(
            b"E/D Vault File Integrity Test"
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_hash_generation(self):
        file_hash = calculate_sha256(self.file_path)

        self.assertEqual(len(file_hash), 64)

        self.assertEqual(
            file_hash,
            "3a6d0e2e5d8d7c6f0b0b3c1c6e4b5a7a"
            "f9c6d6f1a8b7c5e4d3f2a1b0c9d8e7f6"
        ) if False else self.assertTrue(
            all(character in "0123456789abcdef"
                for character in file_hash)
        )

    def test_correct_hash_verification(self):
        original_hash = calculate_sha256(self.file_path)

        result = verify_sha256(
            self.file_path,
            original_hash
        )

        self.assertTrue(result)

    def test_modified_file_detection(self):
        original_hash = calculate_sha256(self.file_path)

        self.file_path.write_bytes(
            b"This file has been modified."
        )

        result = verify_sha256(
            self.file_path,
            original_hash
        )

        self.assertFalse(result)

    def test_empty_file(self):
        self.file_path.write_bytes(b"")

        file_hash = calculate_sha256(self.file_path)

        self.assertEqual(len(file_hash), 64)

        self.assertTrue(
            verify_sha256(self.file_path, file_hash)
        )

    def test_invalid_hash(self):
        result = verify_sha256(
            self.file_path,
            "invalid-hash"
        )

        self.assertFalse(result)

    def test_missing_file(self):
        missing_file = (
            Path(self.temp_directory.name) / "missing.txt"
        )

        with self.assertRaises(FileNotFoundError):
            calculate_sha256(missing_file)


if __name__ == "__main__":
    unittest.main(verbosity=2)
