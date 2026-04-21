from __future__ import annotations
from flask import request
from werkzeug.exceptions import BadRequest

def require_json() -> dict:
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Expected JSON request body.")
    if not isinstance(data, dict):
        raise BadRequest("JSON body must be an object.")
    return data