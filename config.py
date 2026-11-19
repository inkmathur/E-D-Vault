
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "edvault.db"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + DATABASE_PATH.as_posix()
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Maximum upload size
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    # Session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_REFRESH_EACH_REQUEST = False

    # Session cookie security
    SESSION_COOKIE_NAME = "edvault_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
        in ("true", "1", "yes")
    )
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_PATH = "/"
