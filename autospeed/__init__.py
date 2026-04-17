from flask import Flask
from .models import db
from flask_migrate import Migrate
import os
from .auth import init_auth   

migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

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

    #Database
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    #Initializing
    db.init_app(app)
    migrate.init_app(app, db)

    init_auth(app)  # auth owns: csrf, login_manager, oauth, session controls, auth blueprints

    #Register blueprints
    from .errors import register_error_handlers
    register_error_handlers(app)

    from . import entries
    app.register_blueprint(entries.bp)

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from .users import bp as users_bp
    app.register_blueprint(users_bp)

    upload_dir = app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    #Logs at app creation
    app.logger.info("Application created with environment=%s", app.config.get("ENV", "unknown"))
    app.logger.info("Booting app with AUTOSPEED_ENV=%s", os.environ.get("AUTOSPEED_ENV", "development"))

    #Health route for verification of app boot.
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
