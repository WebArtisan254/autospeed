import time
from flask import g, request, current_app

def register_request_logging(app):
    @app.before_request
    def start_time():
        g._start_time = time.time()
        current_app.logger.info(
            "request start %s %s remote=%s",
            request.method,
            request.path,
            request.remote_addr,
        )

        @app.after_request
        def log_response(response):
            dur = int((time.time() - g._start_time) * 1000)
            current_app.logger.info(
                "request end %s %s status=%s dur_ms=%s",
                request.method,
                request.path,
                response.status_code,
                dur,
            )
            return response