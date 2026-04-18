from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import select
from .models import db, Entry
from .api_responses import ok, fail
from .api_validation import validate_entry_create
from .api_serializers import serialize_entry
from flask import g
from .api_auth import load_api_identity
from .rate_limit import limiter
from flask_smorest import Blueprint
from .api_schemas import EntryListResponse, ErrorResponse

bp = Blueprint("api", __name__, url_prefix="/api")


#Rate limiter
limiter.limit("120 per minute; 2000 per hour")(bp)

@bp.get("/entries")
@bp.response(200, EntryListResponse)
@bp.response(401, ErrorResponse)
@bp.response(400, ErrorResponse)

@bp.before_app_request
def authenticate_api():
    user = load_api_identity()
    if user is not None:
        g.api_user = user
    else: 
        g.api_user = None

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
    
    user = g.api_user or (current_user if current_user.is_authenticated else None)
    if user is None:
        return fail(code="auth_required", message="Authentication required.", status=401)

    e = Entry(
        user_id=user.id,
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
    user = g.api_user or (current_user if current_user.is_authenticated else None)
    if user is None:
        return fail(code="auth_required", message="Authentication required.", status=401)
    
    page_raw = request.args.get("page", "1")
    per_page_raw = request.args.get("per_page", "20")
    status_raw = request.args.get("status")
    q = request.args.get("q")

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
        return fail(code="invalid_pagination", message="Page must >= 1.", status=400)
    
    if per_page < 1 or per_page > 100:
        return fail(
            code="invalid_pagination",
            message="per_page must be between 1 and 100.",
            status=400,
        )
    
    filters = [Entry.user_id == user.id]

    if status_raw is not None:
        status = status_raw.strip().lower()
        if status not in {"draft", "published"}:
            return fail(
                code="invalid_filter",
                message="Invalid status filter.",
                status=400,
                details={"status": status_raw},
            )
        filters.append(Entry.status == status)
    
    if q:
        term = f"%{q.strip()}%"
        filters.append(
            (Entry.title.ilike(term)) | (Entry.content.ilike(term))
        )
    
    stmt = (
        select(Entry)
        .where(*filters)
        .order_by(Entry.created_at.desc())
        .offset((page - 1 ) * per_page)
        .limit(per_page + 1)
    )

    items = db.session.scalars(stmt).all()
    has_next = len(items) > per_page
    items = items[:per_page]

    data = [ serialize_entry(e) for e in items]
    meta = {
        "page": page,
        "per_page": per_page,
        "has_next": has_next,
        "status": status_raw,
        "q": q,
    }

    return ok(data=data, meta=meta)