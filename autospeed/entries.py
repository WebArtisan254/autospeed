from flask import Blueprint, render_template, request, make_response, current_app, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from .db_access import list_entries

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
def index():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page") or 1), 1)
    per_page = min(max(int(request.args.get("per_page") or 10), 1), 50)

    entries, total = list_entries(q=q, page=page, per_page=per_page)

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
def create():
    if request.method == "GET":
        return render_template("entries/new.html", title="", errors={})
    
    title, attachment, errors = _validate_entry_form(request.form, request.files)

    if errors:
        current_app.logger.info("Entry create validation failed: %s", errors)
        return render_template("entries/new.html", title=title, errors=errors), 400

    if attachment and attachment.filename:
        safe_name = secure_filename(attachment.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
        attachment.save(upload_path)
        current_app.logger.info("Saved attachment %s", safe_name)

    _ENTRIES.append({
        "id": len(_ENTRIES) + 1, 
        "title": title,
    })

    flash("Entry created.")
    return redirect(url_for("entries.index"))

    

@bp.get("/<int:entry_id>")
def detail(entry_id):
    return render_template("entries/detail.html", entry_id=entry_id)