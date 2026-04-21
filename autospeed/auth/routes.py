from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select
from ..jobs import get_queue
from ..models import EmailOutbox, db, User, ApiToken
from .session import mark_session_issued
from .tokens import issue_token, consume_token
from ..domain.users import register_user, ValidationError as UserValidationError
from rq import Retry

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html", username="", email="", errors={})

    data = {
        "username": request.form.get("username", ""),
        "email": request.form.get("email", ""),
        "password": request.form.get("password", ""),
        "confirm": request.form.get("confirm", ""),
    }

    try:
        user = register_user(data=data)
    except UserValidationError as e:
        return render_template(
            "auth/register.html",
            username=data["username"],
            email=data["email"],
            errors={e.field: e.message},
        ), 400

    login_user(user)
    mark_session_issued()
    flash("Account created. Welcome to my First Web App Project!!")
    return redirect(url_for("entries.index"))

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

@bp.route("/reset", methods=["GET", "POST"])
def reset_request():
    if request.method == "GET":
        return render_template("auth/reset_request.html", email="", errors={})

    email = (request.form.get("email") or "").strip().lower()
    errors = {}
    if not email:
        errors["email"] = "Email is required."
        return render_template("auth/reset_request.html", email=email, errors=errors), 400

    user = db.session.scalars(select(User).where(User.email == email)).first()

    if user:
        raw, tok = issue_token(user=user, purpose="reset", ttl_minutes=15)
        reset_link = url_for("auth.reset_password", token=raw, _external=True)
        current_app.logger.info("Password reset link for %s: %s", email, reset_link)

        dedupe = EmailOutbox.make_dedupe_key(
            kind="password_reset",
            user_id=user.id,
            token_id=tok.id,
        )

        existing = db.session.scalar(
            select(EmailOutbox).where(EmailOutbox.dedupe_key == dedupe)
        )

        if existing is None:
            msg = EmailOutbox(
                dedupe_key=dedupe,
                to_email=user.email,
                subject="Reset your password",
                body=(
                    "You requested a password reset.\n\n"
                    f"Reset your password using this link:\n{reset_link}\n\n"
                    "If you did not request this, you can ignore this email."
                ),
                status="pending",
            )
            db.session.add(msg)
            db.session.commit()

            get_queue().enqueue(
                "autospeed.tasks.email_tasks.deliver_outbox_email",
                outbox_id=msg.id,
                retry=Retry(max=3),
            )

    flash("If an account exists for that email, a reset link has been sent.")
    return redirect(url_for("auth.login"))

@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    if request.method == "GET":
        return render_template("auth/reset_password.html", errors={})

    password = request.form.get("password") or ""
    confirm = request.form.get("confirm") or ""

    errors = {}
    if not password:
        errors["password"] = "Password is required."
    if password and len(password) < 10:
        errors["password"] = "Use at least 10 characters."
    if password != confirm:
        errors["confirm"] = "Passwords do not match."

    if errors:
        return render_template("auth/reset_password.html", errors=errors), 400
    
    tok = consume_token(raw_token=token, purpose="reset")
    if tok is None:
        flash("Reset link is invalid or expired.")
        return redirect(url_for("auth.reset_request"))
    
    user = db.session.get(User, tok.user_id)
    if user is None:
        flash("Reset link is invalid or expired.")
        return redirect(url_for("auth.reset_request"))
    
    user.set_password(password)

    user.session_valid_after = datetime.now(timezone.utc)

    db.session.commit()
    flash("Password updated. Please log in.")
    return redirect(url_for("auth.login"))

@bp.post("/tokens/<int:token_id>/revoke")
@login_required
def revoke_token(token_id):
    tok = db.session.get(ApiToken, token_id)
    if tok is None or tok.user_id != current_user.id:
        flash("Token not found.")
        return redirect(url_for("auth.tokens"))
    
    if tok.revoked_at is not None:
        flash("Token already revoked.")
        return redirect(url_for("auth.tokens"))

    tok.revoked_at = datetime.now(timezone.utc)
    db.session.commit()
    flash("Token revoked.")
    return redirect(url_for("auth.tokens"))


