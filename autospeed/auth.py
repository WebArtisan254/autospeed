from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from sqlalchemy import select 
from flask import Blueprint
from flask_login import LoginManager
from .models import db, User

bp = Blueprint("auth", __name__, url_prefix="/auth")
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id: str):
    try:
        uid = int(user_id)
    except ValueError:
        return None
    
    return db.session.get(User, uid)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html", username="", errors={})
    
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    errors = {}
    if not username:
        errors["username"] = "Username is required."
    if not password:
        errors["password"] = "Password is required."

    if errors:
        return render_template("auth/login.html", username=username, errors=errors), 400
    
    user = db.session.scalars(select(User).where(User.username == username)).first()

    if user is None or not user.check_password(password):
        current_app.logger.info("Failed login for username=%r", username)
        errors["__all__"] = "Invalid username or password."
        return render_template("auth/login.html", username=username, errors=errors), 401
    
    login_user(user)
    flash("You are now logged in.")
    return redirect(url_for("entries.index"))

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.")
    return redirect(url_for("auth.login"))

@bp.get("/ping")
def ping():
    # End points proves blueprint registration works.
    return {"auth": "ok"}