
import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import RequestEntityTooLarge

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=False)

from config import Config, INSTANCE_DIR
from database.db import db
from extensions import limiter

from authentication.routes import auth_bp
from routes.files import files_bp
from routes.activity import activity_bp
from routes.settings import settings_bp

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    secret_key = app.config.get("SECRET_KEY")

    if not secret_key or len(str(secret_key)) < 32:
        raise RuntimeError(
            "SECRET_KEY is missing or too short. "
            "Set a strong key of at least 32 characters in .env."
        )

    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
    app.config["RATELIMIT_HEADERS_ENABLED"] = True

    os.makedirs(INSTANCE_DIR, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(settings_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = (
            "strict-origin-when-cross-origin"
        )
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' "
            "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        )
        return response

    from database import models

    @app.route("/")
    def home():
        if session.get("user_id"):
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("auth.login"))

    @app.route("/health")
    def health():
        return jsonify({
            "status": "healthy",
            "application": "E/D Vault"
        })

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(error):
        flash(
            "Upload rejected. Maximum allowed file size is 100 MB.",
            "danger"
        )
        return redirect(url_for("files.encrypt_upload")), 413

    @app.errorhandler(429)
    def handle_rate_limit(error):
        flash(
            "Too many login attempts. Please wait one minute before trying again.",
            "danger"
        )
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    debug_mode = (
        os.environ.get("FLASK_DEBUG", "false").lower()
        in ("true", "1", "yes")
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=debug_mode
    )
