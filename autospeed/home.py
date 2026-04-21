from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint("home", __name__)

@bp.get("/")
def index():
    return render_template("home.html")