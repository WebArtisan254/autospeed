from __future__ import annotations
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"csv"}

def is_allowed_filename(filename: str) -> bool:
    if not filename:
        return False
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def normalize_filename(filename: str) -> str:
    return secure_filename(filename)