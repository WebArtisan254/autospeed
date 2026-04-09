import os 

class BaseConfig:
    SECRET_KEY = os.environ.get("AUTOSPEED_SECRET_KEY", "dev")

    DATABASE_URL = os.environ.get("AUTOSPEED_DATABASE_URL", "sqlite:///instance/dev.db")

    UPLOAD_FOLDER = os.environ.get("AUTOSPEED_UPLOAD_FOLDER", "uploads")

    USE_PROXY_FIX = os.environ.get("AUTOSPEED_USE_PROXY_FIX", "false").lower() == "true"

#Default    
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DATABASE_URL = BaseConfig.DATABASE_URL or "sqlite:///instance/dev.db"

class StagingConfig(BaseConfig):
    DEBUG = False
    TESTING = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False