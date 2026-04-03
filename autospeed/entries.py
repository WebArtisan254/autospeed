from flask import Blueprint, render_template

bp = Blueprint("entries", __name__, url_prefix="/entries")

@bp.get('/')
def index():
    return render_template("entries/index.html", entries=[])

@bp.get("/new")
def create_form():
    return render_template("entries/new.html")

@bp.post("/new")
def create_submit():
    return "Created", 201

@bp.get("/<int:entry_id>")
def detail(entry_id):
    return render_template("entries/detail.html", entry_id=entry_id)