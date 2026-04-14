import os 

class BaseConfig:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    SECRET_KEY = os.environ.get("AUTOSPEED_SECRET_KEY", "dev")

    DATABASE_URL = os.environ.get("AUTOSPEED_DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'dev.db')}")

    UPLOAD_FOLDER = os.environ.get("AUTOSPEED_UPLOAD_FOLDER", "uploads")

    USE_PROXY_FIX = os.environ.get("AUTOSPEED_USE_PROXY_FIX", "false").lower() == "true"

#Default    
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DATABASE_URL = BaseConfig.DATABASE_URL or f"sqlite:///{BaseConfig.BASE_DIR}/instance/dev.db"

class StagingConfig(BaseConfig):
    DEBUG = False
    TESTING = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"