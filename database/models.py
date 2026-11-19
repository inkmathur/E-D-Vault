
from datetime import datetime, timezone

from database.db import db


def current_utc_time():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=current_utc_time,
        nullable=False
    )

    vault_files = db.relationship(
        "VaultFile",
        backref="owner",
        lazy=True,
        cascade="all, delete-orphan"
    )

    activities = db.relationship(
        "ActivityLog",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class VaultFile(db.Model):
    __tablename__ = "vault_files"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    original_filename = db.Column(
        db.String(255),
        nullable=False
    )

    stored_filename = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=False
    )

    sha256_hash = db.Column(
        db.String(64),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=current_utc_time,
        nullable=False
    )


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    action = db.Column(
        db.String(80),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=current_utc_time,
        nullable=False
    )
