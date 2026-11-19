
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import app


class SecurityHeadersTest(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_content_type_options(self):
        response = self.client.get("/login")
        self.assertEqual(
            response.headers.get("X-Content-Type-Options"),
            "nosniff"
        )

    def test_frame_options(self):
        response = self.client.get("/login")
        self.assertEqual(
            response.headers.get("X-Frame-Options"),
            "DENY"
        )

    def test_referrer_policy(self):
        response = self.client.get("/login")
        self.assertEqual(
            response.headers.get("Referrer-Policy"),
            "strict-origin-when-cross-origin"
        )

    def test_content_security_policy(self):
        response = self.client.get("/login")
        csp = response.headers.get("Content-Security-Policy", "")

        self.assertIn("default-src 'self'", csp)
        self.assertIn("object-src 'none'", csp)
        self.assertIn("frame-ancestors 'none'", csp)

    def test_root_redirect(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main(verbosity=2)
