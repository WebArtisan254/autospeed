from __future__ import annotations
from flask import render_template, request, current_app
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import CSRFError
from .api_responses import fail
from flask_limiter.errors import RateLimitExceeded


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        if is_api_request():
            return api_error(
                code=e.name.lower().replace(" ", "_"),
                message=e.description,
                status=e.code or 500,
            )
        
        return render_template("errors/http.html", error=e), e.code or 500
        
    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        current_app.logger.exception("Unhandled exception")
        if is_api_request():
            return api_error(
                code="internal_error",
                message="An unexpected error occurred.",
                status=500,
            )
        
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template("errors/400.html", message="Your form expired or was invalid. Please try again."), 400
    
    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        if request.path.startswith("/api/"):
            return fail(
                code="rate_limited",
                message="Too many requests. Please slow down.",
                status=429,
                details={"limit": str(e.description)},
            )
        return "Too many requests", 429
    
    def is_api_request() -> bool:
        return request.path.startswith("/api/")
    
    def api_error(*, code: str, message: str, status: int, details: dict | None = None):
        payload = {
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        }
        return payload, status