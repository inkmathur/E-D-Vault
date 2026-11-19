
import logging
import re
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g
)

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from email_validator import validate_email, EmailNotValidError

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database.db import db
from database.models import User
from extensions import limiter


auth_bp = Blueprint("auth", __name__)

logger = logging.getLogger(__name__)

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
MAX_IDENTIFIER_LENGTH = 120

DUMMY_PASSWORD_HASH = generate_password_hash(
    "E_D_Vault_Dummy_Password_Only"
)


def login_required(view_function):
    """Allow access only to authenticated users."""

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Please log in to access this page.",
                "warning"
            )
            return redirect(url_for("auth.login"))

        user = db.session.get(User, user_id)

        if user is None:
            session.clear()

            flash(
                "Your session is no longer valid. Please log in.",
                "warning"
            )

            return redirect(url_for("auth.login"))

        g.current_user = user

        return view_function(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour", methods=["POST"])
def register():

    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip().lower()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        # Username validation
        if not re.fullmatch(
            r"[a-zA-Z0-9_]{3,30}",
            username
        ):
            flash(
                "Username must contain 3–30 letters, "
                "numbers, or underscores.",
                "danger"
            )
            return render_template("register.html")

        # Email validation
        if not email or len(email) > 254:
            flash(
                "Please enter a valid email address.",
                "danger"
            )
            return render_template("register.html")

        try:
            email = validate_email(
                email,
                check_deliverability=False
            ).normalized.lower()

        except EmailNotValidError:
            flash(
                "Please enter a valid email address.",
                "danger"
            )
            return render_template("register.html")

        if len(email) > MAX_IDENTIFIER_LENGTH:
            flash(
                "Email address is too long.",
                "danger"
            )
            return render_template("register.html")

        # Password validation
        if not isinstance(password, str):
            flash("Invalid password.", "danger")
            return render_template("register.html")

        if len(password) < MIN_PASSWORD_LENGTH:
            flash(
                "Password must contain at least 12 characters.",
                "danger"
            )
            return render_template("register.html")

        if len(password) > MAX_PASSWORD_LENGTH:
            flash(
                "Password cannot exceed 128 characters.",
                "danger"
            )
            return render_template("register.html")

        if len(confirm_password) > MAX_PASSWORD_LENGTH:
            flash(
                "Confirmation password is too long.",
                "danger"
            )
            return render_template("register.html")

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )
            return render_template("register.html")

        # Check duplicate account details
        existing_user = User.query.filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

        if existing_user:
            flash(
                "Username or email is already registered.",
                "danger"
            )
            return render_template("register.html")

        # Hash password before database storage
        password_hash = generate_password_hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )

        try:
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            flash(
                "Username or email is already registered.",
                "danger"
            )

            return render_template("register.html")

        except SQLAlchemyError:
            db.session.rollback()

            logger.exception(
                "Database error during user registration."
            )

            flash(
                "Registration could not be completed. Please try again.",
                "danger"
            )

            return render_template("register.html")

        flash(
            "Registration successful. You can now log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():

    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":

        identifier = request.form.get(
            "identifier", ""
        ).strip().lower()

        password = request.form.get("password", "")

        # Input validation
        if (
            not identifier
            or not password
            or len(identifier) > MAX_IDENTIFIER_LENGTH
            or len(password) > MAX_PASSWORD_LENGTH
        ):
            flash(
                "Invalid username/email or password.",
                "danger"
            )
            return render_template("login.html")

        user = User.query.filter(
            or_(
                User.username == identifier,
                User.email == identifier
            )
        ).first()

        # Perform password verification even if the user
        # does not exist, reducing timing differences.
        stored_hash = (
            user.password_hash
            if user is not None
            else DUMMY_PASSWORD_HASH
        )

        password_valid = check_password_hash(
            stored_hash,
            password
        )

        if user is None or not password_valid:
            flash(
                "Invalid username/email or password.",
                "danger"
            )
            return render_template("login.html")

        # Start a fresh authenticated session
        session.clear()

        session["user_id"] = user.id
        session.permanent = True

        flash(
            "Login successful. Welcome to E/D Vault!",
            "success"
        )

        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():

    user = g.current_user

    return render_template(
        "dashboard.html",
        user=user
    )
