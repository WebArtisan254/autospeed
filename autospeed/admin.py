from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import select
from flask_login import current_user
from .models import db, User, EmailOutbox
from .security import require_role
from .domain.users import admin_update_user, delete_user, ValidationError, NotFoundError

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/users")
@require_role("admin")
def users():
    all_users = db.session.scalars(
        select(User).order_by(User.created_at.desc())
    ).all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@require_role("admin")
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        flash("User not found.")
        return redirect(url_for("admin.users"))

    if request.method == "GET":
        return render_template(
            "admin/edit_user.html",
            user=user,
            username=user.username,
            email=user.email,
            role=user.role,
            errors={},
        )

    data = {
        "username": request.form.get("username", ""),
        "email": request.form.get("email", ""),
        "role": request.form.get("role", user.role),
    }

    try:
        admin_update_user(user_id=user_id, data=data)
    except ValidationError as e:
        return render_template(
            "admin/edit_user.html",
            user=user,
            username=data["username"],
            email=data["email"],
            role=data["role"],
            errors={e.field: e.message},
        ), 400

    flash("User updated.")
    return redirect(url_for("admin.users"))


@bp.post("/users/<int:user_id>/role")
@require_role("admin")
def set_role(user_id: int):
    role = (request.form.get("role") or "").strip()

    if role not in {"admin", "member"}:
        flash("Invalid role.")
        return redirect(url_for("admin.users"))

    user = db.session.get(User, user_id)
    if user is None:
        flash("User not found.")
        return redirect(url_for("admin.users"))

    if user.id == current_user.id and role != "admin":
        flash("You cannot remove your own admin access.")
        return redirect(url_for("admin.users"))

    user.role = role
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to update user role")
        flash("Could not update role. Please try again.")
        return redirect(url_for("admin.users"))

    flash("Role updated.")
    return redirect(url_for("admin.users"))


@bp.post("/users/<int:user_id>/delete")
@require_role("admin")
def delete_user_route(user_id):
    if user_id == current_user.id:
        flash("You cannot delete yourself.")
        return redirect(url_for("admin.users"))

    try:
        delete_user(user_id=user_id)
    except NotFoundError:
        flash("User not found.")
        return redirect(url_for("admin.users"))

    flash("User deleted.")
    return redirect(url_for("admin.users"))


@bp.route("/email-outbox")
@require_role("admin")
def email_outbox():
    msgs = db.session.scalars(
        select(EmailOutbox).order_by(EmailOutbox.created_at.desc()).limit(100)
    ).all()
    return render_template("admin/email_outbox.html", msgs=msgs)
