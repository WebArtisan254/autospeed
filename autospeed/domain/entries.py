from typing import Mapping
from sqlalchemy import select
from ..models import db, Entry

class EntryError(Exception):
    pass

class ValidationError(EntryError):
    def __init__(self, field: str, message: str):
        self.field = field 
        self.message = message

def create_entry_for_user(*, user_id: int, data: Mapping[str, str]) -> Entry:
    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()
    status = (data.get("status") or "draft").strip().lower()

    if not title:
        raise ValidationError("title", "Title is required.")
    
    if status not in {"draft", "published"}:
        raise ValidationError("status", "Invalid status value.")
    
    entry = Entry(
        user_id=user_id,
        title=title,
        content=content,
        status=status,
    )

    db.session.add(entry)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return entry