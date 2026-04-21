from __future__ import annotations
import uuid
from pathlib import Path
from flask import current_app

def upload_dir() -> Path:
    base = current_app.config.get("UPLOAD_DIR", "var/uploads")
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_upload(file_storage, *, original_name: str) -> str:
    key = f"{uuid.uuid4().hex}.bin"
    path = upload_dir() / key
    file_storage.save(path)
    return key

def open_upload(key: str, mode: str = "rb"):
    path = upload_dir() / key
    return open(path, mode)