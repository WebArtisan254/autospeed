from flask import Blueprint, render_template, request, make_response, current_app, flash, redirect, url_for

bp = Blueprint("entries", __name__, url_prefix="/entries")

@bp.get('/')
def index():
    return render_template("entries/index.html", entries=[])

@bp.get("/new")
def create_form():
    return render_template("entries/new.html")

@bp.post("/new")
def create_submit():
    #Read input from request
    title = request.form.get("title")

    #Log received
    current_app.logger.info("Create entry request with title=%r", title)

    if not title:
        #Construct a response explicitly for a bad request
        resp = make_response("Title is required", 400)
        return resp
    
    flash("Entry created.")
    return redirect(url_for("entries.index"))
    

@bp.get("/<int:entry_id>")
def detail(entry_id):
    return render_template("entries/detail.html", entry_id=entry_id)