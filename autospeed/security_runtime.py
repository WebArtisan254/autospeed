from datetime import datetime, timestamp
from flask import session
from flask_login import current_user, logout_user

def register_session_controls(app):
    @app.before_request
    def enforce_session_validity():
        if not current_user.is_authenticated:
            return 
        
        issued_at = session.get("auth_issued_at")
        if issued_at is None:
            logout_user()
            return
        
        issued_dt = datetime.utcfromtimestamp(float(issued_at))

        if issued_dt < current_user.session_valid_after:
            logout_user()
            session.clear()