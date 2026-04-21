from flask import render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import select 
from flask import Blueprint
from flask_login import LoginManager
from .models import db, User, EmailOutbox
from .db_access import issue_user_token, consume_user_token
from datetime import datetime, timezone
from .jobs import get_queue

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
    session["auth_issued_at"] = datetime.now(timezone.utc).timestamp()
    flash("You are now logged in.")
    return redirect(url_for("entries.index"))

@bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You are now logged out.")
    return redirect(url_for("auth.login"))

@bp.post("/verify/request")
@login_required
def request_verification():
    if current_user.email_verified:
        return redirect(url_for("users.me"))
    
    raw = issue_user_token(user=current_user, purpose="verify", ttl_minutes=30)
    link = url_for("auth.verify_email", token=raw, _external=True)

    current_app.logger.info("Verification link for %s: %s", current_user.email, link)
    flash("Verification link generated. Check your email in production; in development it is logged.")
    return redirect(url_for("users.me"))

@bp.get("/verify/<token>")
@login_required
def verify_email(token: str):
    tok = consume_user_token(raw_token=token, purpose="verify")
    if tok is None or tok.user_id != current_user.id:
        flash("Verification link is invalid or expired.")
        return redirect(url_for("users.me"))
    
    current_user.email_verified = True
    db.session.commit()
    flash("Email verified.")
    return redirect(url_for("users.me"))

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
        raw, tok = issue_user_token(user=user, purpose="reset", ttl_minutes=15)
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
                retry=3,
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
    
    tok = consume_user_token(raw_token=token, purpose="reset")
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

@bp.get("/ping")
def ping():
    # End points proves blueprint registration works.
    return {"auth": "ok"}