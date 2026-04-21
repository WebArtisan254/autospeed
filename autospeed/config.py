import os 
from dotenv import load_dotenv

class BaseConfig:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    SECRET_KEY = os.environ.get("AUTOSPEED_SECRET_KEY", "dev")

    DATABASE_URL = os.environ.get("AUTOSPEED_DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'dev.db')}")

    UPLOAD_FOLDER = os.environ.get("AUTOSPEED_UPLOAD_FOLDER", "uploads")

    USE_PROXY_FIX = os.environ.get("AUTOSPEED_USE_PROXY_FIX", "false").lower() == "true"

    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_ID_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    CORS_ALLOWED_ORIGINS = []

#Default    
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DATABASE_URL = BaseConfig.DATABASE_URL or f"sqlite:///{BaseConfig.BASE_DIR}/instance/dev.db"

    CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]

    SMTP_HOST = "localhost"
    SMTP_PORT = 1025
    SMTP_USERNAME = ""
    SMTP_PASSWORD = ""
    SMTP_SENDER = "dev@example.test"

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

    CORS_ALLOWED_ORIGINS = ["https://autospeed.com"]

    SMTP_HOST = "smtp.yourprovider.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "apikey"
    #SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]
    SMTP_SENDER = "no-reply@autospeed.com"

    REQUIRE_HTTPS = True

    MAX_CONTENT_LENGTH = 10 * 1024 *  1024