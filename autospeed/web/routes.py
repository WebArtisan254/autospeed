from __future__ import annotations
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import select
from ..jobs import get_queue
from ..models import db, ImportJob, EmailOutbox
from ..domain.entries import create_entry_for_user, ValidationError
from ..storage import save_upload

bp = Blueprint("web", __name__)

@bp.route("/entries/new", methods=["GET", "POST"])
@login_required
def new_entry():
    if request.method == "POST":
        try:
            create_entry_for_user(
                user_id=current_user.id,
                data=request.form,
            )
            flash("Entry created.")
            return redirect(url_for("web.entries"))
        except ValidationError as e:
            flash(e.message)

    return render_template("entries/new.html")


@bp.route("/imports", methods=["GET", "POST"])
@login_required
def imports():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please choose a file.")
            return redirect(url_for("web.imports"))

        storage_key, original_name = save_upload(file)

        job = ImportJob(
            user_id=current_user.id,
            storage_key=storage_key,
            filename=original_name,
            status="pending",
        )
        db.session.add(job)
        db.session.commit()

        get_queue().enqueue(
            "autospeed.tasks.import_tasks.process_import_v1",
            payload={"v": 1, "job_id": job.id},
            retry=1,
        )

        return redirect(url_for("web.import_status", job_id=job.id))

    jobs = db.session.scalars(
        select(ImportJob)
        .where(ImportJob.user_id == current_user.id)
        .order_by(ImportJob.created_at.desc())
    ).all()
    return render_template("imports/index.html", jobs=jobs)


@bp.route("/imports/<int:job_id>")
@login_required
def import_status(job_id: int):
    job = db.session.get(ImportJob, job_id)
    if job is None or job.user_id != current_user.id:
        abort(404)
    return render_template("imports/status.html", job=job)


@bp.route("/activity")
@login_required
def activity():
    imports = db.session.scalars(
        select(ImportJob)
        .where(ImportJob.user_id == current_user.id)
        .order_by(ImportJob.created_at.desc())
        .limit(20)
    ).all()

    outbox = db.session.scalars(
        select(EmailOutbox)
        .where(EmailOutbox.to_email == current_user.email)
        .order_by(EmailOutbox.created_at.desc())
        .limit(20)
    ).all()

    return render_template("activity.html", imports=imports, outbox=outbox)

@bp.post("/imports/<int:job_id>/retry")
@login_required
def retry_import(job_id):
    job = db.session.get(ImportJob, job_id)
    if job is None or job.user_id != current_user.id:
        abort(404)

    if job.status != "failed":
        flash("Only failed imports can be retried.")
        return redirect(url_for("web.import_status", job_id=job_id))
    
    job.status = "pending"
    job.error = None
    job.processed = 0
    job.total = None
    db.session.commit()

    get_queue().enqueue(
        "autospeed.tasks.import_tasks.process_import_v1",
        payload={"v": 1, "job_id": job.id},
        retry=1,
    )

    flash("Import retry started.")
    return redirect(url_for("web.import_status", job_id=job_id))