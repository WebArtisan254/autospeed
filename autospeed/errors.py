from flask import render_template, request, current_app
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import CSRFError
from .api_responses import fail


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if request.path.startswith("/api/"):
            return fail(code=f"http_{e.code}", message=e.description, status=e.code)
        return e

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        current_app.logger.exception("Unhandled exception")
        if request.path.startswith("/api/"):
            return fail(code="internal_error", message="An unexpected error occurred.", status=500)
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template("errors/400.html", message="Your form expired or was invalid. Please try again."), 400
    