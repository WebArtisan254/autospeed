def normalize_status(kind: str, status: str) -> str:
    if kind == "email":
        if status in {"pending"}:
            return "pending"
        if status in {"sending"}:
            return "running"
        if status in {"sent"}:
            return "completed"
        if status in {"failed"}:
            return "failed"
    return status