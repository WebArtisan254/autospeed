import os 

# Absolute path to the directory where this config.py file lives
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-later'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Settings used when FLASK_CONFIG=development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
            os.environ.get('DEV_DATABASE_URI')
            or 'sqlite:///' + os.path.join(basedir, 'app.db')
    )

class ProductionConfig(Config):
    """Settings used when FLASK_CONFIG=production."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')

# Map environment names to config classes
config = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
}
