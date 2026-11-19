
import sys
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from database.db import db
from sqlalchemy import text, inspect


class DatabaseSecurityTest(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_sqlite_foreign_keys_enabled(self):
        with db.engine.connect() as connection:
            result = connection.execute(
                text("PRAGMA foreign_keys")
            ).scalar()

        self.assertEqual(result, 1)

    def test_database_foreign_key_constraints_exist(self):
        inspector = inspect(db.engine)

        vault_keys = inspector.get_foreign_keys("vault_files")
        activity_keys = inspector.get_foreign_keys("activity_logs")

        self.assertGreater(len(vault_keys), 0)
        self.assertGreater(len(activity_keys), 0)

    def test_no_existing_foreign_key_violations(self):
        with db.engine.connect() as connection:
            violations = connection.execute(
                text("PRAGMA foreign_key_check")
            ).fetchall()

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
