from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import select
from .models import db, Entry

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.get("/entries")
@login_required
def list_entries():
    try:
        page = int(request.args.get("page", "1"))
        per_page = int(request.args.get("per_page", "20"))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400
    
    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)

    stmt = (
        select(Entry)
        .where(Entry.user_id == current_user.id)
        .order_by(Entry.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page + 1)
    )

    items = db.session.scalars(stmt).all()
    has_next = len(items) > per_page
    items = items[:per_page]

    payload = {
        "page": page, 
        "per_page": per_page, 
        "has_next": has_next, 
        "items": [
            {
                "id": e.id,
                "title": e.title,
                "status": e.status, 
                "created_at": e.created_at.isoformat() + "Z",
            }
            for e in items
        ],
    }
    return jsonify(payload), 200