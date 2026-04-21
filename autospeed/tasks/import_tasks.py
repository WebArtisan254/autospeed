from __future__ import annotations

import csv
from flask import current_app

from ..models import db, ImportJob, Entry
from ..storage import open_for_read


def process_import_v1(*, payload: dict) -> None:
    v = payload.get("v")
    job_id = payload.get("job_id")

    if v != 1 or not isinstance(job_id, int):
        current_app.logger.error("Invalid import payload: %r", payload)
        return

    job = db.session.get(ImportJob, job_id)
    if job is None or job.status not in {"pending", "running"}:
        return

    if job.status == "pending":
        job.status = "running"
        db.session.commit()

    try:
        with open_for_read(job.storage_key) as f:
            text = (line.decode("utf-8") for line in f)
            rows = list(csv.DictReader(text))

        job.total = len(rows)
        db.session.commit()

        for idx, row in enumerate(rows, start=1):
            entry = Entry(
                user_id=job.user_id,
                title=(row.get("title") or "").strip(),
                status=(row.get("status") or "draft").strip().lower(),
            )
            db.session.add(entry)
            job.processed = idx

            if idx % 50 == 0:
                db.session.commit()

        job.status = "completed"
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        job = db.session.get(ImportJob, job_id)
        if job:
            job.status = "failed"
            job.error = str(e)
            db.session.commit()
        current_app.logger.exception("Import job %s failed", job_id)
        raise
