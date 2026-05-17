from __future__ import annotations
from functools import wraps
from typing import Callable, Any
from flask import abort
from flask_login import current_user, login_required

def require_role(*roles: str):
    def decorator(view: Callable[..., Any]):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if getattr(current_user, "role", None) not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator