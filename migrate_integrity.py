
from sqlalchemy import inspect, text

from app import app
from database.db import db


with app.app_context():

    inspector = inspect(db.engine)

    columns = {
        column["name"]
        for column in inspector.get_columns("vault_files")
    }

    if "sha256_hash" not in columns:

        db.session.execute(
            text(
                "ALTER TABLE vault_files "
                "ADD COLUMN sha256_hash VARCHAR(64)"
            )
        )

        db.session.commit()

        print("SUCCESS: SHA-256 column added to vault_files.")

    else:

        print("INFO: SHA-256 column already exists.")

print("Integrity database migration completed.")
