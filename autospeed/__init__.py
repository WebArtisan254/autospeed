from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    #Safe default for development
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    if test_config is not None:
        app.config.from_mapping(test_config)
    else:
        app.config.from_prefixed_env()

    #Initialize extensions
    #from .extensions import db
    #db.init_app(app)

    #Register BluePrints 
    from . import auth
    app.register_blueprint(auth.bp)

    #Health route for verification of app boot. 
    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app