from flask import Flask
from .routes import bp as auth_bp
from ..oauth import bp as oauth_bp, init_oauth
from .session import register_session_controls
from ..forms import csrf
from .login import login_manager

def init_auth(app: Flask) -> None:
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    init_oauth(app)

    register_session_controls(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(oauth_bp)