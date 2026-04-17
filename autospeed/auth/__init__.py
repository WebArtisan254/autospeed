from flask import Flask
from ..oauth import bp as oauth_bp, init_oauth
from .session import register_session_controls
from ..forms import csrf
from .login import login_manager
from flask import request, jsonify, redirect, url_for

def init_auth(app: Flask) -> None:
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith("/api"):
            return jsonify({"error": "Authentication"}), 401
        return redirect(url_for("auth.login"))
    
    #Initializing
    init_oauth(app)

    register_session_controls(app)

    #Registering Blueprints
    from .routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    app.register_blueprint(oauth_bp)