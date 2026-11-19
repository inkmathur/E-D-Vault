
import hashlib
import tempfile
import unittest

from pathlib import Path

from encryption.encrypt import encrypt_file
from encryption.decrypt import decrypt_file


class EncryptionTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)

        self.original_file = self.folder / "original.txt"
        self.original_data = b"E/D Vault encryption test file."

        self.original_file.write_bytes(self.original_data)

        self.encrypted_file = self.folder / "original.txt.edv"
        self.decrypted_file = self.folder / "recovered.txt"

        self.password = "TestPassword@123"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_encrypt_and_decrypt(self):
        encrypt_file(
            self.original_file,
            self.password,
            self.encrypted_file
        )

        decrypt_file(
            self.encrypted_file,
            self.password,
            self.decrypted_file
        )

        self.assertEqual(
            self.original_file.read_bytes(),
            self.decrypted_file.read_bytes()
        )

    def test_wrong_password(self):
        encrypt_file(
            self.original_file,
            self.password,
            self.encrypted_file
        )

        with self.assertRaisesRegex(ValueError, "incorrect password"):
            decrypt_file(
                self.encrypted_file,
                "WrongPassword@123",
                self.decrypted_file
            )

        self.assertFalse(self.decrypted_file.exists())

    def test_tampered_file(self):
        encrypt_file(
            self.original_file,
            self.password,
            self.encrypted_file
        )

        data = bytearray(self.encrypted_file.read_bytes())
        data[-1] ^= 1
        self.encrypted_file.write_bytes(data)

        with self.assertRaisesRegex(ValueError, "incorrect password"):
            decrypt_file(
                self.encrypted_file,
                self.password,
                self.decrypted_file
            )

        self.assertFalse(self.decrypted_file.exists())

    def test_unique_encryption_output(self):
        second_file = self.folder / "second.edv"

        encrypt_file(
            self.original_file,
            self.password,
            self.encrypted_file
        )

        encrypt_file(
            self.original_file,
            self.password,
            second_file
        )

        self.assertNotEqual(
            self.encrypted_file.read_bytes(),
            second_file.read_bytes()
        )

    def test_empty_password_rejected(self):
        with self.assertRaises(ValueError):
            encrypt_file(
                self.original_file,
                "",
                self.encrypted_file
            )


if __name__ == "__main__":
    unittest.main()
