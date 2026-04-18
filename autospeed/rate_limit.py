from __future__ import annotations
from flask import request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user

def _api_rate_limit_key() -> str:
    user = getattr(g, "api_user", None) or (current_user if current_user.is_authenticated else None)
    if user is not None:
        return f"user:{user.id}"
    return f"ip:{get_remote_address()}"

limiter = Limiter(
    key_func=_api_rate_limit_key,
    default_limits=[],
)