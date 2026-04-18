from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import select
from .models import db, Entry
from .api_responses import ok, fail
from .api_validation import validate_entry_create
from .api_serializers import serialize_entry

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.post("/entries")
@login_required
def create_entry():
    payload = request.get_json(silent=True)

    clean, errors = validate_entry_create(payload)
    if errors:
        return fail(
            code="validation_failed",
            message="Your request body is invalid.",
            status=400,
            details=errors,
        )
    
    e = Entry(
        user_id=current_user.id,
        title=clean["title"],
        content=clean["content"],
        status=clean["status"],
    )

    db.session.add(e)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to create entry")
        return fail(code="db_error", message="Could not create entry.", status=500)
    
    return ok(data=serialize_entry(e), status=201)

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

    data = [serialize_entry(e) for e in items]

    meta = {"page": page, "per_page": per_page, "has_next": has_next}
    
    return ok(data=data, meta=meta)