from flask import render_template
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return render_template("errors/http.html", error=e), e.code