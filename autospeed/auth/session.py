from datetime import datetime, timezone
from flask import session
from flask_login import current_user, logout_user

def mark_session_issued() -> None:
    session["auth_issued_at"] = datetime.now(timezone.utc).timestamp()

def register_session_controls(app):
    @app.before_request
    def enforce_session_validity():
        if not current_user.is_authenticated:
            return

        issued_at = session.get("auth_issued_at")
        if issued_at is None:
            logout_user()
            session.clear()
            return

        issued_dt = datetime.fromtimestamp(float(issued_at), tz=timezone.utc)

        valid_after = current_user.session_valid_after
        if valid_after.tzinfo is None:
            valid_after = valid_after.replace(tzinfo=timezone.utc)

        if issued_dt < valid_after:
            logout_user()
            session.clear()

