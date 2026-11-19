
import unittest

from encryption.key_manager import (
    generate_salt,
    generate_nonce,
    derive_key,
    KEY_LENGTH,
    SALT_LENGTH,
    NONCE_LENGTH
)


class TestKeyManager(unittest.TestCase):

    def test_salt_generation(self):
        salt = generate_salt()

        self.assertEqual(len(salt), SALT_LENGTH)

    def test_nonce_generation(self):
        nonce = generate_nonce()

        self.assertEqual(len(nonce), NONCE_LENGTH)

    def test_key_generation(self):
        salt = generate_salt()
        key = derive_key("StrongPassword123!", salt)

        self.assertEqual(len(key), KEY_LENGTH)

    def test_same_password_and_salt(self):
        salt = generate_salt()

        key1 = derive_key("StrongPassword123!", salt)
        key2 = derive_key("StrongPassword123!", salt)

        self.assertEqual(key1, key2)

    def test_different_salts(self):
        salt1 = generate_salt()
        salt2 = generate_salt()

        key1 = derive_key("StrongPassword123!", salt1)
        key2 = derive_key("StrongPassword123!", salt2)

        self.assertNotEqual(key1, key2)

    def test_empty_password_rejected(self):
        with self.assertRaises(ValueError):
            derive_key("", generate_salt())

    def test_invalid_salt_rejected(self):
        with self.assertRaises(ValueError):
            derive_key("StrongPassword123!", b"invalid")

    def test_long_password_rejected(self):
        with self.assertRaises(ValueError):
            derive_key("A" * 1025, generate_salt())


if __name__ == "__main__":
    unittest.main()
