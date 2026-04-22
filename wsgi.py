from logging.config import dictConfig

dictConfig({
    "version": 1, 
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["wsgi"]
    }
})

from autospeed import create_app
import os

env = os.getenv("AUTOSPEED_ENV", "development")

config_map = {
    "production": "autospeed.config.ProductionConfig",
    "staging": "autospeed.config.StagingConfig",
    "development": "autospeed.config.DevelopmentConfig",
    "test": "autospeed.config.TestConfig",
}

app = create_app(config_map.get(env, "autospeed.config.DevelopmentConfig"))
