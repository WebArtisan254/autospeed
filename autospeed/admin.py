from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from sqlalchemy import select
from .models import db, User
from .security import require_role
from flask_login import current_user

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.get("/users")
@require_role("admin")
def users():
    items = db.session.scalars(select(User).order_by(User.created_at.desc())).all()
    return render_template("admin/users.html", users=items)

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
        flash("Could not update role. Please try again")
        return redirect(url_for("admin.users"))
    
    flash("Role updated.")
    return redirect(url_for("admin.users"))
