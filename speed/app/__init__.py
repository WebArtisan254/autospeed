from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from config import config 

db = SQLAlchemy()
bootstrap = Bootstrap5()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions 
    db.init_app(app)
    bootstrap.init_app(app)
    
    # Import the blueprint object from the main package.
    # 'main' is the blueprint instance created in app/main/__init__.py.
    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


