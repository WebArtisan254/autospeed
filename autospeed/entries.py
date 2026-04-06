from flask import Blueprint, render_template, request, make_response, current_app, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename

bp = Blueprint("entries", __name__, url_prefix="/entries")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.get('/')
def index():
    return render_template("entries/index.html", entries=[])

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
    
    filename = None

    if attachment and attachment.filename:
        safe_name = secure_filename(attachment.filename)

        if not safe_name:
            return render_template(
                "entries/new.html",
                title=title,
                errors={"attachment": "Invalid filename."}
            ), 400
        
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], safe_name)
        attachment.save(upload_path)

        filename = safe_name
        current_app.logger.info("Saved attachment as %s", filename)
    
    current_app.logger.info("Entry validated and accepted: title=%r", title)

    flash("Entry created.")
    return redirect(url_for("entries.index"))
    

@bp.get("/<int:entry_id>")
def detail(entry_id):
    return render_template("entries/detail.html", entry_id=entry_id)