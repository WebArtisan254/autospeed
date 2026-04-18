from __future__ import annotations
from flask import jsonify
from typing import Any, Mapping

def ok(*, data: Any = None, meta: Mapping[str, Any] | None = None, status: int = 200):
    payload: dict[str, Any] = {"data": data}
    if meta is not None:
        payload["meta"] = dict(meta)
    return jsonify(payload), status

def fail(*, code: str, message: str, status: int, details: Mapping[str, Any] | None = None):
    payload: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = dict(details)
    return jsonify(payload), status