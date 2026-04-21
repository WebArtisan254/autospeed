from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from ..models import db, User, ApiToken
from .session import mark_session_issued
from .tokens import issue_token, consume_token

bp = Blueprint("auth", __name__, url_prefix="/auth")

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
    if user is None or user.password_hash is None or not user.check_password(password):
        current_app.logger.info("Failed login for username=%r", username)
        errors["__all__"] = "Invalid username or password."
        return render_template("auth/login.html", username=username, errors=errors), 401
    
    login_user(user)
    mark_session_issued()
    flash("You are now logged in.")
    return redirect(url_for("entries.index"))

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.")
    return redirect(url_for("auth.login"))

@bp.route("/tokens", methods=["GET", "POST"])
@login_required
def tokens():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Token name is required.")
            return redirect(url_for("auth.tokens"))
        
        raw = ApiToken.generate()
        tok = ApiToken(
            user_id=current_user.id,
            name=name,
            token_hash=ApiToken.hash(raw),
        )
        db.session.add(tok)
        db.session.commit()

        return render_template("auth/token_created.html", token=raw)
    
    tokens = db.session.scalars(
        select(ApiToken).where(ApiToken.user_id == current_user.id, ApiToken.revoked_at.is_(None))
    ).all()
    return render_template("auth/tokens.html", tokens=tokens)

