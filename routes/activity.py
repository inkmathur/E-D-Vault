
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from database.db import db
from database.models import User, ActivityLog
from authentication.routes import login_required


activity_bp = Blueprint("activity", __name__)


ACTIVITY_TYPES = {
    "FILE_ENCRYPTED": "File Encrypted",
    "FILE_DECRYPTED": "File Decrypted",
    "FILE_DOWNLOADED": "File Downloaded",
    "FILE_DELETED": "File Deleted",
    "FILE_INTEGRITY_CHECKED": "Integrity Checked"
}

MAX_SEARCH_LENGTH = 255


def get_activity_count(user_id, action):
    """Count a specific activity type for one user."""

    return ActivityLog.query.filter_by(
        user_id=user_id,
        action=action
    ).count()


def escape_search_query(value):
    """Escape SQL LIKE wildcard characters in user input."""

    return (
        value
        .replace("!", "!!")
        .replace("%", "!%")
        .replace("_", "!_")
    )


@activity_bp.route("/activity")
@login_required
def history():

    user_id = session.get("user_id")
    user = db.session.get(User, user_id)

    if not user:

        session.clear()

        return redirect(url_for("auth.login"))

    # Read and validate filter inputs.
    selected_action = request.args.get(
        "action",
        ""
    ).strip()[:80]

    search_query = request.args.get(
        "search",
        ""
    ).strip()[:MAX_SEARCH_LENGTH]

    # Always restrict records to the current user.
    query = ActivityLog.query.filter_by(
        user_id=user.id
    )

    # Filter by a recognized activity type only.
    if selected_action in ACTIVITY_TYPES:

        query = query.filter_by(
            action=selected_action
        )

    else:

        selected_action = ""

    # Search by filename.
    if search_query:

        safe_search = escape_search_query(search_query)

        query = query.filter(
            ActivityLog.filename.ilike(
                f"%{safe_search}%",
                escape="!"
            )
        )

    # Display the latest 100 matching records.
    activities = (
        query
        .order_by(
            ActivityLog.created_at.desc(),
            ActivityLog.id.desc()
        )
        .limit(100)
        .all()
    )

    # Count only the current user's activities.
    total_activities = ActivityLog.query.filter_by(
        user_id=user.id
    ).count()

    encrypted_count = get_activity_count(
        user.id,
        "FILE_ENCRYPTED"
    )

    decrypted_count = get_activity_count(
        user.id,
        "FILE_DECRYPTED"
    )

    download_count = get_activity_count(
        user.id,
        "FILE_DOWNLOADED"
    )

    deleted_count = get_activity_count(
        user.id,
        "FILE_DELETED"
    )

    integrity_count = get_activity_count(
        user.id,
        "FILE_INTEGRITY_CHECKED"
    )

    return render_template(
        "activity.html",
        activities=activities,
        activity_types=ACTIVITY_TYPES,
        selected_action=selected_action,
        search_query=search_query,
        total_activities=total_activities,
        encrypted_count=encrypted_count,
        decrypted_count=decrypted_count,
        download_count=download_count,
        deleted_count=deleted_count,
        integrity_count=integrity_count
    )
