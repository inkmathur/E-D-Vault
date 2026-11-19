
import logging
import re
import shutil
import tempfile
import uuid

from pathlib import Path

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from database.db import db
from database.models import User, VaultFile, ActivityLog
from authentication.routes import login_required
from extensions import limiter

from encryption.encrypt import encrypt_file, MAX_FILE_SIZE
from encryption.decrypt import decrypt_file

from integrity.hash_manager import (
    calculate_sha256,
    verify_sha256
)


files_bp = Blueprint("files", __name__)

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
ENCRYPTED_DIR = BASE_DIR / "storage" / "encrypted"

UPLOAD_CHUNK_SIZE = 1024 * 1024
MAX_FILENAME_LENGTH = 255
MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

STORED_FILENAME_PATTERN = re.compile(
    r"^[0-9a-f]{32}\.edv$"
)


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def get_current_user():
    """Return the currently authenticated user."""

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


def verify_account_password(user, password):
    """Verify the account login password."""

    if (
        not user
        or not isinstance(password, str)
        or not password
        or len(password) > MAX_PASSWORD_LENGTH
    ):
        return False

    return check_password_hash(
        user.password_hash,
        password
    )


def validate_original_filename(filename):
    """Convert an uploaded filename into a safe filename."""

    if not isinstance(filename, str):
        return None

    if not filename or len(filename) > 1024:
        return None

    safe_name = secure_filename(filename)

    if not safe_name:
        return None

    if len(safe_name) > MAX_FILENAME_LENGTH:
        return None

    if safe_name in (".", ".."):
        return None

    return safe_name


def get_encrypted_file_path(stored_filename):
    """
    Resolve an encrypted file safely.

    Only UUID-based .edv filenames are accepted.
    Files outside encrypted storage and symbolic links
    are rejected.
    """

    if not isinstance(stored_filename, str):
        return None

    if not STORED_FILENAME_PATTERN.fullmatch(stored_filename):
        return None

    try:
        storage_directory = ENCRYPTED_DIR.resolve(strict=True)

        file_path = storage_directory / stored_filename

        if file_path.is_symlink():
            return None

        resolved_path = file_path.resolve(strict=True)

        if resolved_path.parent != storage_directory:
            return None

        if not resolved_path.is_file():
            return None

        return resolved_path

    except (OSError, RuntimeError):
        return None


def save_upload_with_limit(uploaded_file, destination):
    """
    Save an uploaded file in chunks.

    Stop immediately if the file exceeds MAX_FILE_SIZE.
    """

    total_size = 0

    with destination.open("xb") as output_file:

        while True:

            chunk = uploaded_file.stream.read(
                UPLOAD_CHUNK_SIZE
            )

            if not chunk:
                break

            total_size += len(chunk)

            if total_size > MAX_FILE_SIZE:
                raise ValueError("FILE_SIZE_LIMIT_EXCEEDED")

            output_file.write(chunk)

    return total_size


def get_safe_download_name(filename):
    """Return a safe filename for a decrypted download."""

    safe_name = validate_original_filename(filename)

    if not safe_name:
        return "decrypted_file"

    return safe_name


def cleanup_directory(directory):
    """Remove a temporary directory safely."""

    if directory:
        shutil.rmtree(
            directory,
            ignore_errors=True
        )


def verify_vault_file(vault_file, encrypted_path):
    """
    Verify stored file size and SHA-256 fingerprint.

    Old files without a SHA-256 baseline can still be
    checked against their recorded file size.
    """

    try:
        if not encrypted_path.is_file():
            return False

        actual_size = encrypted_path.stat().st_size

        if actual_size != vault_file.file_size:
            return False

        if vault_file.sha256_hash:
            return verify_sha256(
                encrypted_path,
                vault_file.sha256_hash
            )

        return True

    except (OSError, ValueError, TypeError):
        return False


def get_owned_vault_file(file_id, user):
    """Return a vault file only if it belongs to the user."""

    if not user or not file_id:
        return None

    return VaultFile.query.filter_by(
        id=file_id,
        user_id=user.id
    ).first()


def validate_encryption_password(password, confirmation):
    """
    Validate the encryption password on the server.

    Browser-side validation is not trusted.
    """

    if not isinstance(password, str):
        return "Invalid encryption password."

    if not isinstance(confirmation, str):
        return "Invalid password confirmation."

    if not password or not confirmation:
        return "Please complete both encryption password fields."

    if len(password) < MIN_PASSWORD_LENGTH:
        return "Encryption password must contain at least 12 characters."

    if len(password) > MAX_PASSWORD_LENGTH:
        return "Encryption password cannot exceed 128 characters."

    if len(confirmation) > MAX_PASSWORD_LENGTH:
        return "Password confirmation cannot exceed 128 characters."

    if password != confirmation:
        return "Encryption passwords do not match."

    return None


# ---------------------------------------------------------
# ENCRYPT FILE
# ---------------------------------------------------------

@files_bp.route("/encrypt", methods=["GET", "POST"])
@login_required
@limiter.limit("20 per hour", methods=["POST"])
def encrypt_upload():

    if request.method == "GET":
        return render_template("encrypt.html")

    user = get_current_user()

    if not user:
        session.clear()

        flash(
            "Please log in again.",
            "danger"
        )

        return redirect(url_for("auth.login"))

    uploaded_file = request.files.get("file")

    password = request.form.get(
        "encryption_password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    if not uploaded_file or not uploaded_file.filename:

        flash(
            "Please select a file to encrypt.",
            "danger"
        )

        return redirect(url_for("files.encrypt_upload"))

    # IMPORTANT: Validate both passwords on the server.
    password_error = validate_encryption_password(
        password,
        confirm_password
    )

    if password_error:

        flash(
            password_error,
            "danger"
        )

        return redirect(url_for("files.encrypt_upload"))

    original_filename = validate_original_filename(
        uploaded_file.filename
    )

    if not original_filename:

        flash(
            "The selected filename is invalid or too long.",
            "danger"
        )

        return redirect(url_for("files.encrypt_upload"))

    INSTANCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ENCRYPTED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_directory = None
    output_path = None

    try:

        temporary_directory = tempfile.mkdtemp(
            prefix="edvault-upload-",
            dir=INSTANCE_DIR
        )

        temporary_input = (
            Path(temporary_directory)
            / "uploaded_input.tmp"
        )

        actual_size = save_upload_with_limit(
            uploaded_file,
            temporary_input
        )

        if actual_size > MAX_FILE_SIZE:
            raise ValueError("FILE_SIZE_LIMIT_EXCEEDED")

        stored_filename = uuid.uuid4().hex + ".edv"

        output_path = ENCRYPTED_DIR / stored_filename

        encrypt_file(
            input_path=temporary_input,
            password=password,
            output_path=output_path
        )

        encrypted_hash = calculate_sha256(output_path)

        vault_file = VaultFile(
            user_id=user.id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_size=output_path.stat().st_size,
            sha256_hash=encrypted_hash
        )

        activity = ActivityLog(
            user_id=user.id,
            action="FILE_ENCRYPTED",
            filename=original_filename
        )

        db.session.add(vault_file)
        db.session.add(activity)
        db.session.commit()

        flash(
            "File encrypted successfully. SHA-256 integrity fingerprint saved.",
            "success"
        )

        return redirect(url_for("files.my_vault"))

    except ValueError as error:

        db.session.rollback()

        if output_path and output_path.exists():
            output_path.unlink(missing_ok=True)

        if str(error) == "FILE_SIZE_LIMIT_EXCEEDED":

            flash(
                "File is too large. Maximum allowed size is 100 MB.",
                "danger"
            )

        else:

            logger.exception(
                "File upload or encryption validation failed."
            )

            flash(
                "The selected file could not be processed.",
                "danger"
            )

        return redirect(url_for("files.encrypt_upload"))

    except Exception:

        db.session.rollback()

        if output_path and output_path.exists():
            output_path.unlink(missing_ok=True)

        logger.exception(
            "File encryption operation failed."
        )

        flash(
            "Encryption failed. Please check the file and try again.",
            "danger"
        )

        return redirect(url_for("files.encrypt_upload"))

    finally:

        cleanup_directory(temporary_directory)


# ---------------------------------------------------------
# DECRYPT FILE
# ---------------------------------------------------------

@files_bp.route("/decrypt", methods=["GET", "POST"])
@login_required
@limiter.limit("20 per hour", methods=["POST"])
def decrypt_upload():

    user = get_current_user()

    if not user:

        session.clear()

        flash(
            "Please log in again.",
            "danger"
        )

        return redirect(url_for("auth.login"))

    vault_files = (
        VaultFile.query
        .filter_by(user_id=user.id)
        .order_by(VaultFile.created_at.desc())
        .all()
    )

    if request.method == "GET":

        return render_template(
            "decrypt.html",
            vault_files=vault_files
        )

    file_id = request.form.get(
        "file_id",
        type=int
    )

    password = request.form.get(
        "encryption_password",
        ""
    )

    if not file_id:

        flash(
            "Please select a file to decrypt.",
            "danger"
        )

        return redirect(url_for("files.decrypt_upload"))

    if (
        not password
        or len(password) > MAX_PASSWORD_LENGTH
    ):

        flash(
            "Enter the file encryption password.",
            "danger"
        )

        return redirect(url_for("files.decrypt_upload"))

    vault_file = get_owned_vault_file(file_id, user)

    if not vault_file:

        flash(
            "The selected file was not found in your vault.",
            "danger"
        )

        return redirect(url_for("files.decrypt_upload"))

    encrypted_path = get_encrypted_file_path(
        vault_file.stored_filename
    )

    if not encrypted_path:

        flash(
            "The encrypted file could not be found or its storage path is invalid.",
            "danger"
        )

        return redirect(url_for("files.decrypt_upload"))

    if not verify_vault_file(vault_file, encrypted_path):

        flash(
            "Decryption blocked: the encrypted file failed its integrity check.",
            "danger"
        )

        return redirect(url_for("files.decrypt_upload"))

    INSTANCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_directory = None

    try:

        temporary_directory = tempfile.mkdtemp(
            prefix="edvault-decrypt-",
            dir=INSTANCE_DIR
        )

        safe_download_name = get_safe_download_name(
            vault_file.original_filename
        )

        output_path = (
            Path(temporary_directory)
            / "decrypted_output.tmp"
        )

        decrypt_file(
            input_path=encrypted_path,
            password=password,
            output_path=output_path
        )

        activity = ActivityLog(
            user_id=user.id,
            action="FILE_DECRYPTED",
            filename=safe_download_name
        )

        db.session.add(activity)
        db.session.commit()

        response = send_file(
            output_path,
            as_attachment=True,
            download_name=safe_download_name,
            mimetype="application/octet-stream"
        )

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.call_on_close(
            lambda: cleanup_directory(temporary_directory)
        )

        return response

    except Exception:

        db.session.rollback()

        cleanup_directory(temporary_directory)

        logger.exception(
            "File decryption operation failed."
        )

        flash(
            "Decryption failed. The password may be incorrect or the file may be damaged.",
            "danger"
        )

        return redirect(url_for("files.decrypt_upload"))


# ---------------------------------------------------------
# MY VAULT
# ---------------------------------------------------------

@files_bp.route("/vault")
@login_required
def my_vault():

    user = get_current_user()

    if not user:

        session.clear()

        flash(
            "Please log in again.",
            "danger"
        )

        return redirect(url_for("auth.login"))

    vault_files = (
        VaultFile.query
        .filter_by(user_id=user.id)
        .order_by(VaultFile.created_at.desc())
        .all()
    )

    return render_template(
        "vault.html",
        vault_files=vault_files
    )


# ---------------------------------------------------------
# VERIFY FILE INTEGRITY
# ---------------------------------------------------------

@files_bp.route(
    "/vault/<int:file_id>/verify",
    methods=["POST"]
)
@login_required
def verify_file_integrity(file_id):

    user = get_current_user()

    if not user:

        session.clear()

        flash(
            "Please log in again.",
            "danger"
        )

        return redirect(url_for("auth.login"))

    vault_file = get_owned_vault_file(file_id, user)

    if not vault_file:

        flash(
            "File not found in your vault.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    if not vault_file.sha256_hash:

        flash(
            "SHA-256 integrity baseline unavailable for this older file.",
            "warning"
        )

        return redirect(url_for("files.my_vault"))

    encrypted_path = get_encrypted_file_path(
        vault_file.stored_filename
    )

    if not encrypted_path:

        flash(
            "Integrity verification failed: encrypted file is missing or its storage path is invalid.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    try:

        is_intact = verify_vault_file(
            vault_file,
            encrypted_path
        )

        activity = ActivityLog(
            user_id=user.id,
            action="FILE_INTEGRITY_CHECKED",
            filename=vault_file.original_filename
        )

        db.session.add(activity)
        db.session.commit()

        if is_intact:

            flash(
                "INTEGRITY VERIFIED: The encrypted file matches its saved fingerprint.",
                "success"
            )

        else:

            flash(
                "WARNING: The encrypted file has changed since its integrity fingerprint was saved.",
                "danger"
            )

    except Exception:

        db.session.rollback()

        logger.exception(
            "File integrity verification failed."
        )

        flash(
            "Could not complete the integrity verification.",
            "danger"
        )

    return redirect(url_for("files.my_vault"))


# ---------------------------------------------------------
# DOWNLOAD ENCRYPTED FILE
# ---------------------------------------------------------

@files_bp.route(
    "/vault/<int:file_id>/download",
    methods=["POST"]
)
@login_required
def download_encrypted_file(file_id):

    user = get_current_user()

    if not user:

        session.clear()

        flash(
            "Please log in again.",
            "danger"
        )

        return redirect(url_for("auth.login"))

    vault_file = get_owned_vault_file(file_id, user)

    if not vault_file:

        flash(
            "File not found in your vault.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    encrypted_path = get_encrypted_file_path(
        vault_file.stored_filename
    )

    if not encrypted_path:

        flash(
            "The encrypted file could not be found.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    encryption_password = request.form.get(
        "encryption_password",
        ""
    )

    if (
        not encryption_password
        or len(encryption_password) > MAX_PASSWORD_LENGTH
    ):

        flash(
            "Enter the file encryption password to download this file.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    INSTANCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        if not verify_vault_file(vault_file, encrypted_path):

            flash(
                "Download blocked: the encrypted file failed its integrity check.",
                "danger"
            )

            return redirect(url_for("files.my_vault"))

        # Verify AES-GCM authentication before downloading.
        with tempfile.TemporaryDirectory(
            prefix="edvault-verify-",
            dir=INSTANCE_DIR
        ) as temporary_directory:

            verification_output = (
                Path(temporary_directory)
                / "verified_plaintext.tmp"
            )

            decrypt_file(
                input_path=encrypted_path,
                password=encryption_password,
                output_path=verification_output
            )

    except Exception:

        logger.exception(
            "Encrypted file download verification failed."
        )

        flash(
            "Password verification failed or the encrypted file may be damaged. Download was not allowed.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    try:

        activity = ActivityLog(
            user_id=user.id,
            action="FILE_DOWNLOADED",
            filename=vault_file.original_filename
        )

        db.session.add(activity)
        db.session.commit()

    except Exception:

        db.session.rollback()

        logger.exception(
            "Could not record encrypted file download activity."
        )

        flash(
            "Could not record the download activity.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    return send_file(
        encrypted_path,
        as_attachment=True,
        download_name=vault_file.stored_filename,
        mimetype="application/octet-stream"
    )


# ---------------------------------------------------------
# DELETE FILE
# ---------------------------------------------------------

@files_bp.route(
    "/vault/<int:file_id>/delete",
    methods=["POST"]
)
@login_required
def delete_vault_file(file_id):

    user = get_current_user()

    if not user:

        session.clear()

        flash(
            "Please log in again.",
            "danger"
        )

        return redirect(url_for("auth.login"))

    account_password = request.form.get(
        "account_password",
        ""
    )

    if not verify_account_password(
        user,
        account_password
    ):

        flash(
            "Incorrect account password. File was not deleted.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    vault_file = get_owned_vault_file(file_id, user)

    if not vault_file:

        flash(
            "File not found in your vault.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    encrypted_path = get_encrypted_file_path(
        vault_file.stored_filename
    )

    if not encrypted_path:

        flash(
            "The encrypted file could not be found. Nothing was deleted.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    tombstone_path = encrypted_path.with_name(
        encrypted_path.name
        + ".deleting-"
        + uuid.uuid4().hex
    )

    try:

        # Move the file first so a database failure can be rolled back.
        encrypted_path.rename(tombstone_path)

        activity = ActivityLog(
            user_id=user.id,
            action="FILE_DELETED",
            filename=vault_file.original_filename
        )

        db.session.add(activity)
        db.session.delete(vault_file)
        db.session.commit()

    except Exception:

        db.session.rollback()

        if tombstone_path.exists():

            try:
                tombstone_path.rename(encrypted_path)

            except OSError:

                logger.exception(
                    "Could not restore encrypted file after deletion failure."
                )

        logger.exception(
            "Vault file deletion failed."
        )

        flash(
            "File deletion failed. Please try again.",
            "danger"
        )

        return redirect(url_for("files.my_vault"))

    try:

        tombstone_path.unlink(missing_ok=True)

    except OSError:

        logger.exception(
            "Could not remove deleted encrypted file."
        )

    flash(
        "File deleted successfully from your vault.",
        "success"
    )

    return redirect(url_for("files.my_vault"))
