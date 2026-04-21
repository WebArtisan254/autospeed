from typing import Mapping
from sqlalchemy import select
from ..models import db, Entry

class EntryError(Exception):
    pass

class ValidationError(EntryError):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message

class NotFoundError(EntryError):
    pass

class ForbiddenError(EntryError):
    pass

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

def update_entry_for_user(*, user_id: int, entry_id: int, data: Mapping[str, str]) -> Entry:
    entry = db.session.get(Entry, entry_id)
    if entry is None:
        raise NotFoundError("Entry not found.")
    if entry.user_id != user_id:
        raise ForbiddenError("You do not own this entry.")

    title = (data.get("title") or "").strip()
    content = data.get("content")
    status = data.get("status")

    if not title:
        raise ValidationError("title", "Title is required.")
    if len(title) > 120:
        raise ValidationError("title", "Title must be 120 characters or fewer.")

    entry.title = title

    if content is not None:
        entry.content = content.strip()

    if status is not None:
        status = status.strip().lower()
        if status not in {"draft", "published"}:
            raise ValidationError("status", "Invalid status value.")
        entry.status = status

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return entry

def delete_entry_for_user(*, user_id: int, entry_id: int) -> None:
    entry = db.session.get(Entry, entry_id)
    if entry is None:
        raise NotFoundError("Entry not found.")
    if entry.user_id != user_id:
        raise ForbiddenError("You do not own this entry.")

    db.session.delete(entry)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
