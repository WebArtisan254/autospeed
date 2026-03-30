from flask import Blueprint

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.get("/ping")
def ping():
    # End points proves blueprint registration works.
    return {"auth": "ok"}