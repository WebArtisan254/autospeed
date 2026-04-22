from flask import Flask, request, redirect
from .models import db
from flask_migrate import Migrate
import os
from .auth import init_auth
from .rate_limit import limiter   
from .cors import init_cors
from flask_smorest import Api
from .api_docs import api
from .logging import configure_logging

migrate = Migrate()

def create_app(config_object=None, test_config=None):
    app = Flask(__name__)
    configure_logging(app)

    if config_object:
        app.config.from_object(config_object)
    else:
        env = os.environ.get("AUTOSPEED_ENV", "development").lower()

        if env == "production":
            from .config import ProductionConfig as Config
        elif env == "staging":
            from .config import StagingConfig as Config
        else:
            from .config import DevelopmentConfig as Config

        app.config.from_object(Config)

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile("application.cfg", silent=True)

    app.config.from_prefixed_env()

    # HTTPS redirect for production
    if app.config.get("REQUIRE_HTTPS"):
        @app.before_request
        def _redirect_http():
            if request.headers.get("X-Forwarded-Proto", "http") != "https":
                url = request.url.replace("http://", "https://", 1)
                return redirect(url, code=301)

    # Security headers
    @app.after_request
    def _set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    # Database Configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # OpenAPI Configurations
    app.config.update(
        API_TITLE="AutoSpeed Api",
        API_VERSION="1.0",
        OPENAPI_VERSION="3.0.3",
        OPENAPI_URL_PREFIX="/docs",
        OPENAPI_SWAGGER_UI_PATH="/swagger",
        OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
    )

    # Initializing
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    init_cors(app)
    api.init_app(app)
    init_auth(app)

    # Register blueprints
    from .errors import register_error_handlers
    register_error_handlers(app)

    from . import entries
    app.register_blueprint(entries.bp)

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from .users import bp as users_bp
    app.register_blueprint(users_bp)

    from .api import bp as api_bp
    app.register_blueprint(api_bp)

    from .forms import csrf
    csrf.exempt(api_bp)

    from .home import bp as home_bp
    app.register_blueprint(home_bp)

    upload_dir = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    # Logs at app creation
    env = os.environ.get("AUTOSPEED_ENV", "development")
    app.logger.info("Application created with environment=%s", env)
    app.logger.info("Booting app with AUTOSPEED_ENV=%s", env)

    # Health route for verification of app boot
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
