from flask import request, g
from sqlalchemy import select
from .models import db, ApiToken, User

def load_api_identity():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer"):
        return None
    
    raw = header.removeprefix("Bearer").strip()
    if not raw:
        return None
    
    token_hash = ApiToken.hash(raw)

    tok = db.session.scalars(
        select(ApiToken)
        .where(ApiToken.token_hash == token_hash)
        .where(ApiToken.revoked_at.is_(None))
    ).first()

    if tok is None:
        return None
    
    user = db.session.get(User, tok.user_id)
    return user