from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required, logout_user
from .db_access import get_user_with_entries
from .domain.users import update_user_profile, delete_user, ValidationError, NotFoundError

bp = Blueprint("users", __name__, url_prefix="/users")

@bp.get("/me")
@login_required
def me():
    user = get_user_with_entries(current_user.id)
    return render_template("users/me.html", user=user)

@bp.route("/me/edit", methods=["GET", "POST"])
@login_required
def edit_me():
    if request.method == "GET":
        return render_template(
            "users/edit.html",
            username=current_user.username,
            email=current_user.email,
            errors={},
        )

    data = {
        "username": request.form.get("username", ""),
        "email": request.form.get("email", ""),
    }

    try:
        update_user_profile(user_id=current_user.id, data=data)
    except ValidationError as e:
        return render_template(
            "users/edit.html",
            username=data["username"],
            email=data["email"],
            errors={e.field: e.message},
        ), 400

    flash("Profile updated.")
    return redirect(url_for("users.me"))

@bp.post("/me/delete")
@login_required
def delete_me():
    user_id = current_user.id
    logout_user()
    delete_user(user_id=user_id)
    flash("Your account has been deleted.")
    return redirect(url_for("auth.login"))
