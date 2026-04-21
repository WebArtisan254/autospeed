from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from ..models import db, User, User_Token

def _ensure_utc(dt: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes — assume they are UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def issue_token(*, user: User, purpose: str, ttl_minutes: int) -> tuple[str, User_Token]:
    raw = User_Token.generate_token()
    tok = User_Token(
        user_id=user.id,
        purpose=purpose,
        token_hash=User_Token.hash_token(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes),
        used_at=None,
    )
    db.session.add(tok)
    db.session.commit()
    return raw, tok

def consume_token(*, raw_token: str, purpose: str) -> User_Token | None:
    tok = db.session.scalars(
        select(User_Token)
        .where(User_Token.token_hash == User_Token.hash_token(raw_token))
        .where(User_Token.purpose == purpose)
    ).first()

    if tok is None:
        return None

    now = datetime.now(timezone.utc)
    expires_at = _ensure_utc(tok.expires_at)
    used_at = _ensure_utc(tok.used_at)

    if used_at is not None or expires_at < now:
        return None

    tok.used_at = now
    db.session.commit()
    return tok

