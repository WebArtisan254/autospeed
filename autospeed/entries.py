from flask import Blueprint, render_template, request, make_response, current_app, flash, redirect, url_for
import os
from .db_access import create_entry, list_entries, get_entry
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from .domain.entries import (
    create_entry_for_user,
    update_entry_for_user,
    delete_entry_for_user,
    NotFoundError,
    ForbiddenError,
    ValidationError,
)

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
    content = (form.get("content") or "").strip()

    errors = {}

    if not title:
        errors["title"] = "Title is required."
    if title and len(title) > 120:
        errors["title"] = "Title must be 120 characters or fewer."

    attachment = files.get("attachment")
    if attachment and attachment.filename:
        if not _allowed_file(attachment.filename):
            errors["attachment"] = "Unsupported file type."

    return title, content, attachment, errors


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "GET":
        return render_template("entries/new.html", title="", content="", errors={})

    title, content, upload, errors = _validate_entry_form(request.form, request.files)

    if errors:
        return render_template("entries/new.html", title=title, content=content, errors=errors), 400

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
            user_id=current_user.id,
            title=title,
            content=content,
            attachment_filename=safe_name,
            attachment_original_name=original_name,
        )
    except Exception:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        current_app.logger.exception("Failed to create entry")
        errors = {"__all__": "Could not save entry. Please try again."}
        return render_template("entries/new.html", title=title, content=content, errors=errors), 500

    flash("Entry created.")
    return redirect(url_for("entries.index"))


@bp.get("/<int:entry_id>")
@login_required
def detail(entry_id):
    entry = get_entry(entry_id)
    if entry is None:
        flash("Entry not found.")
        return redirect(url_for("entries.index"))
    if entry.user_id != current_user.id:
        flash("You do not own this entry.")
        return redirect(url_for("entries.index"))

    return render_template("entries/detail.html", entry=entry)


@bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit(entry_id):
    entry = get_entry(entry_id)
    if entry is None:
        flash("Entry not found.")
        return redirect(url_for("entries.index"))
    if entry.user_id != current_user.id:
        flash("You do not own this entry.")
        return redirect(url_for("entries.index"))

    if request.method == "GET":
        return render_template(
            "entries/edit.html",
            entry=entry,
            title=entry.title,
            content=entry.content,
            status=entry.status,
            errors={},
        )

    data = {
        "title": request.form.get("title", ""),
        "content": request.form.get("content", ""),
        "status": request.form.get("status", entry.status),
    }

    try:
        update_entry_for_user(user_id=current_user.id, entry_id=entry_id, data=data)
    except ValidationError as e:
        return render_template(
            "entries/edit.html",
            entry=entry,
            title=data["title"],
            content=data["content"],
            status=data["status"],
            errors={e.field: e.message},
        ), 400

    flash("Entry updated.")
    return redirect(url_for("entries.detail", entry_id=entry_id))

@bp.post("/<int:entry_id>/delete")
@login_required
def delete(entry_id):
    try:
        delete_entry_for_user(user_id=current_user.id, entry_id=entry_id)
    except (NotFoundError, ForbiddenError):
        flash("Could not delete entry.")
        return redirect(url_for("entries.index"))

    flash("Entry deleted.")
    return redirect(url_for("entries.index"))