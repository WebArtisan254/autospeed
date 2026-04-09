from flask import Blueprint, render_template, g
from .db_access import get_user_with_entries

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get("/me")
def me():
    user = get_user_with_entries(g.current_user.id)
    return render_template("users/me.html", user=user)