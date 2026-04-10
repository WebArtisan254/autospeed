from flask import Blueprint, render_template, request, make_response, current_app, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from .db_access import create_entry, list_entries
from flask_login import current_user, login_required

bp = Blueprint("entries", __name__, url_prefix="/entries")

_DEMO_ENTRIES = [
    {"id": i, "title": f"Entry {i}"} for i in range(1, 101)
]

_ENTRIES = []

def _parse_int(value, default, minimum=None, maximum=None):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    if minimum is not None and n < minimum:
        return default
    if maximum is not None and n > maximum:
        return default
    return n

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.get('/')
@login_required
def index():
    q = (request.args.get("q") or "").strip()

    try:
        page = int(request.args.get("page") or 1)
    except ValueError:
        page = 1
    page = max(page, 1)

    try:
        per_page = int(request.args.get("per_page") or 10)
    except ValueError:
        per_page = 10
    per_page = min(max(per_page, 1), 50)

    entries, total = list_entries(
        user_id=current_user.id, 
        q=q, 
        page=page,
        per_page=per_page,
    )

    has_prev = page > 1
    has_next = page * per_page < total

    return render_template(
        "entries/index.html",
        entries=entries,
        q=q,
        page=page,
        per_page=per_page,
        total=total,
        has_prev=has_prev,
        has_next=has_next,
    )

def _validate_entry_form(form, files):
    title = (form.get("title") or "").strip()

    errors = {}

    if not title:
        errors["title"] = "Title is required."

    if title and len(title) > 120:
        errors["title"] = "Title must be 120 characters or fewer."

    attachment = files.get("attachment")

    if attachment and attachment.filename:
        if not _allowed_file(attachment.filename):
            errors["attachment"] = "Unsupported file type."

    return title, attachment, errors

@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("entries/new.html", title="", errors={})
    
    title, upload, errors = _validate_entry_form(request.form, request.files)

    if errors:
        return render_template("entries/new.html", title=title, errors=errors), 400
    
    safe_name = None
    original_name = None
    file_path = None

    if upload and upload.filename:
        safe_name = secure_filename(upload.filename)
        original_name = upload.filename
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)

    try:
        if file_path:
            upload.save(file_path)
        
        create_entry(
            user_id = current_user.id,
            title=title, 
            attachment_filename=safe_name,
            attachment_original_name=original_name,
        )
    
    except Exception:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        current_app.logger.exception("Failed to create entry")
        errors = {"__all__": "Could not save entry. Please try again."}
        return render_template("entries/new.html", title=title, errors=errors), 500


    flash("Entry created.")
    return redirect(url_for("entries.index"))

    

@bp.get("/<int:entry_id>")
def detail(entry_id):
    return render_template("entries/detail.html", entry_id=entry_id)