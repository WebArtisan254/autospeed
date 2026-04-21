from __future__ import annotations

def require_int(payload: dict, key: str) -> int:
    val = payload.get(key)
    if not isinstance(val, int):
        raise ValueError(f"{key} must int")
    return val

def require_version(payload: dict, expected: int) -> None:
    v = payload.get("v")
    if v != expected:
        raise ValueError("Unsupported payload version")