import os 

class BaseConfig:
    #Default
    SECRET_KEY = os.environ.get("AUTOSPEED_SECRET_KEY", "dev")

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

class StagingConfig(BaseConfig):
    DEBUG = False
    TESTING = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False