from flask import Blueprint, render_template
from flask_login import current_user, login_required
from .db_access import get_user_with_entries

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get("/me")
@login_required
def me():
    user = get_user_with_entries(current_user.id)
    return render_template("users/me.html", user=user)