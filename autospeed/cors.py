from flask_cors import CORS

def init_cors(app):
    allowed = app.config.get("CORS_ALLOWED_ORIGINS", [])
    if not allowed:
        return
    
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed}},
        supports_credentials=False,
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,
    )