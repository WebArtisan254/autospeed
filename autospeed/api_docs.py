from flask import Blueprint
from flask_smorest import Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

