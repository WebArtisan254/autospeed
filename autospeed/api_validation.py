from __future__ import annotations
from typing import Any

ALLOWED_ENTRY_STATUSES = {"draft", "published"}

def validate_entry_create(payload: Any):
    if not isinstance(payload, dict):
        return None, {"__all__": "JSON object expected."}
    
    title = payload.get("title")
    content = payload.get("content", "")
    status = payload.get("status", "draft")

    errors: dict[str, str] = {}

    if not isinstance(title, str) or not title.strip():
        errors["title"] = "Title is required."
    elif len(title.strip()) > 40:
        errors["title"] = "Title must be 40 characters or fewer."
    
    if content is None:
        content = ""
    if not isinstance(content, str):
        errors["content"] = "Content must be a string."
    elif len(content) > 20_000:
        errors["content"] = "Content is too long."
    if not isinstance(status, str):
        errors["status"] = "Status must be a string."
    else:
        status = status.strip().lower()
        if status not in ALLOWED_ENTRY_STATUSES:
            errors["status"] = "Status must be 'draft' or 'published'."
    
    if errors:
        return None, errors
    
    clean = {
        "title": title.strip(),
        "content": content,
        "status": status,
    }
    return clean, None