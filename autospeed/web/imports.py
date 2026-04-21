from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from autospeed.security.uploads import is_allowed_filename, normalize_filename
from autospeed.storage.uploads import save_upload
from autospeed.models import db, ImportJob
from autospeed.domain.audit import record_event
from autospeed.domain.async_work import enqueue_import

bp = Blueprint("imports", __name__)

@bp.route("/imports", methods=["POST"])
@login_required
def create_import():
    f = request.files.get("file")
    if not f or not f.filename:
        flash("Choose a file to upload.", "error")
        return redirect(url_for("imports.page"))

    original = f.filename
    safe_name = normalize_filename(original)

    if not is_allowed_filename(safe_name):
        flash("Only CSV files are allowed.", "error")
        return redirect(url_for("imports.page"))

    storage_key = save_upload(f, original_name=safe_name)

    job = ImportJob(
        user_id=current_user.id,
        original_filename=safe_name,
        storage_key=storage_key,
        status="pending",
    )
    db.session.add(job)
    db.session.flush()

    record_event(
        event_type="import.uploaded",
        object_type="import_job",
        object_id=str(job.id),
        actor_user_id=current_user.id,
        metadata={"filename": safe_name},
    )

    enqueue_import(job.id)
    db.session.commit()
    flash("Import started. You can track progress on the status page.", "success")
    return redirect(url_for("imports.status", job_id=job.id))
