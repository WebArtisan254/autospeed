from flask import Blueprint, request, g
from flask_login import current_user
from sqlalchemy import select
from .models import db, Entry
from .api_responses import ok, fail
from .api_serializers import serialize_entry
from .api_auth import load_api_identity
from .rate_limit import limiter
from .domain.entries import create_entry_for_user, ValidationError, update_entry_for_user, delete_entry_for_user, NotFoundError, ForbiddenError

bp = Blueprint("api", __name__, url_prefix="/api")

limiter.limit("120 per minute; 2000 per hour")(bp)

@bp.before_app_request
def authenticate_api():
    g.api_user = load_api_identity()

def _get_user():
    return g.api_user or (current_user if current_user.is_authenticated else None)

@bp.post("/entries")
def create_entry():
    user = _get_user()
    if user is None:
        return fail(code="auth_required", message="Authentication required.", status=401)

    payload = request.get_json(silent=True) or {}
    try:
        entry = create_entry_for_user(user_id=user.id, data=payload)
    except ValidationError as e:
        return fail(
            code="validation_error",
            message=e.message,
            status=400,
            details={"field": e.field},
        )
    return ok(data=serialize_entry(entry), status=201)

@bp.get("/entries")
def list_entries():
    user = _get_user()
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
        .offset((page - 1) * per_page)
        .limit(per_page + 1)
    )

    items = db.session.scalars(stmt).all()
    has_next = len(items) > per_page
    items = items[:per_page]

    data = [serialize_entry(e) for e in items]
    meta = {
        "page": page,
        "per_page": per_page,
        "has_next": has_next,
        "status": status_raw,
        "q": q,
    }

    return ok(data=data, meta=meta)


@bp.put("/entries/<int:entry_id>")
def update_entry(entry_id):
    user = _get_user()
    if user is None:
        return fail(code="auth_required", message="Authentication required.", status=401)

    payload = request.get_json(silent=True) or {}
    try:
        entry = update_entry_for_user(user_id=user.id, entry_id=entry_id, data=payload)
    except NotFoundError:
        return fail(code="not_found", message="Entry not found.", status=404)
    except ForbiddenError:
        return fail(code="forbidden", message="You do not own this entry.", status=403)
    except ValidationError as e:
        return fail(
            code="validation_error",
            message=e.message,
            status=400,
            details={"field": e.field},
        )
    return ok(data=serialize_entry(entry))

@bp.delete("/entries/<int:entry_id>")
def delete_entry(entry_id):
    user = _get_user()
    if user is None:
        return fail(code="auth_required", message="Authentication required.", status=401)

    try:
        delete_entry_for_user(user_id=user.id, entry_id=entry_id)
    except NotFoundError:
        return fail(code="not_found", message="Entry not found.", status=404)
    except ForbiddenError:
        return fail(code="forbidden", message="You do not own this entry.", status=403)

    return ok(data={"deleted": entry_id})
