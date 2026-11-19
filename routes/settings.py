
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from sqlalchemy.exc import SQLAlchemyError

from database.db import db
from database.models import User
from authentication.routes import login_required
from extensions import limiter


settings_bp = Blueprint("settings", __name__)

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
@limiter.limit("5 per hour", methods=["POST"])
def security_settings():

    user_id = session.get("user_id")
    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        flash("Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        current_password = request.form.get(
            "current_password", ""
        )

        new_password = request.form.get(
            "new_password", ""
        )

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        # Check that all fields are provided.
        if not current_password or not new_password or not confirm_password:
            flash("Please complete all password fields.", "danger")
            return redirect(url_for("settings.security_settings"))

        # Reject oversized values before password hashing.
        if len(current_password) > MAX_PASSWORD_LENGTH:
            flash("The current password is invalid.", "danger")
            return redirect(url_for("settings.security_settings"))

        if len(new_password) > MAX_PASSWORD_LENGTH:
            flash(
                "Your new password cannot exceed 128 characters.",
                "danger"
            )
            return redirect(url_for("settings.security_settings"))

        if len(confirm_password) > MAX_PASSWORD_LENGTH:
            flash("Password confirmation is too long.", "danger")
            return redirect(url_for("settings.security_settings"))

        # Verify the existing account password.
        if not check_password_hash(
            user.password_hash,
            current_password
        ):
            flash("Your current password is incorrect.", "danger")
            return redirect(url_for("settings.security_settings"))

        # Validate the new password length.
        if len(new_password) < MIN_PASSWORD_LENGTH:
            flash(
                "Your new password must contain at least 12 characters.",
                "danger"
            )
            return redirect(url_for("settings.security_settings"))

        # Confirm that both new password fields match.
        if new_password != confirm_password:
            flash("The new passwords do not match.", "danger")
            return redirect(url_for("settings.security_settings"))

        # Prevent reusing the current password.
        if new_password == current_password:
            flash(
                "Your new password must be different from your current password.",
                "danger"
            )
            return redirect(url_for("settings.security_settings"))

        # Generate a secure password hash.
        try:
            user.password_hash = generate_password_hash(
                new_password
            )

            db.session.commit()

        except SQLAlchemyError:
            db.session.rollback()

            flash(
                "Password change failed due to a database error. Please try again.",
                "danger"
            )

            return redirect(url_for("settings.security_settings"))

        # Log out the current session after password change.
        session.clear()

        flash(
            "Your password has been changed successfully. Please log in again.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "settings.html",
        user=user
    )
