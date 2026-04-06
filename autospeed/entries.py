from flask import Blueprint, render_template, request, make_response, current_app, flash, redirect, url_for

bp = Blueprint("entries", __name__, url_prefix="/entries")

@bp.get('/')
def index():
    return render_template("entries/index.html", entries=[])

def _validate_entry_form(form):
    title = (form.get("title") or "").strip()

    errors = {}

    if not title:
        errors["title"] = "Title is required."

    if title and len(title) > 120:
        errors["title"] = "Title must be 120 characters or fewer."

    return title, errors

@bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("entries/new.html", title="", errors={})
    
    title, errors = _validate_entry_form(request.form)

    if errors:
        current_app.logger.info("Entry create validation failed: %s", errors)
        return render_template("entries/new.html", title=title, errors=errors), 400
    
    current_app.logger.info("Entry validated and accepted: title=%r", title)

    flash("Entry created.")
    return redirect(url_for("entries.index"))
    

@bp.get("/<int:entry_id>")
def detail(entry_id):
    return render_template("entries/detail.html", entry_id=entry_id)