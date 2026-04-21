from __future__ import annotations
from .models import Entry

def serialize_entry(e: Entry) -> dict:
    return {
        "id": e.id,
        "title": e.title,
        "content": e.content,
        "status": e.status,
        "created_at": e.created_at.isoformat() + "Z",
        "update_at": e.update_at.isoformat() + "Z" if e.update_at else None,
    }
