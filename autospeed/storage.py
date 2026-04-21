from __future__ import annotations
import os
import uuid
from pathlib import Path
from werkzeug.datastructures import FileStorage

def save_upload(file: FileStorage) -> tuple[str, str]:
    upload_dir = Path(os.environ.get("UPLOAD_DIR", "instance/uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)

    key = f"uploads/{uuid.uuid4().hex}"
    filename = file.filename or "upload.bin"
    path = upload_dir / key.replace("/", "_")
    file.save(path)

    return key, filename

def open_for_read(storage_key: str):
    upload_dir = Path(os.environ.get("UPLOAD_DIR", "instance/uploads"))
    path = upload_dir / storage_key.replace("/", "_")
    return open(path, "rb")
