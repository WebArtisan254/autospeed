from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import select
from .models import db, Entry
from .api_responses import ok, fail

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.get("/entries")
@login_required
def list_entries():
    page_raw = request.args.get("page", "1")
    per_page_raw = request.args.get("per_page", "20")

    try:
        page = int(page_raw)
        per_page = int(per_page_raw)
    except ValueError:
        return fail(
            code="invalid_pagination",
            message="Pagination parameters must be integers.",
            status=400, 
            details={"page": page_raw, "per_page": per_page_raw},
        )
    
    if page < 1:
        return fail(
            code="invalid_pagination",
            message="Page must be >= 1.",
            status=400,
            details={"page": page},
        )
    
    if per_page < 1 or per_page > 100:
        return fail(
            code="invalid_pagination",
            message="per_page must be between 1 and 100.",
            status=400,
            details={"per_page": per_page},
        )
    
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

    data = [
        {
            "id": e.id,
            "title": e.title,
            "status": e.status,
            "created_at": e.created_at.isoformat() + "Z",
        }
        for e in items
    ]

    meta = {"page": page, "per_page": per_page, "has_next": has_next}
    return ok(data=data, meta=meta)