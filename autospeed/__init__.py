from flask import Flask
import os

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

    if test_config is None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile("application.cfg", silent=True)

    app.config.from_prefixed_env()

    #Register blueprints
    from . import auth
    app.register_blueprint(auth.bp)

    #Health route for verification of app boot. 
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app