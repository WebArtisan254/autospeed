from sqlalchemy import select
from flask import render_template
from ..admin import bp, require_role
from ..models import db, EmailOutbox

@bp.route("/email-outbox")
@require_role("admin")
def email_outbox():
    msgs = db.session.scalars(
        select(EmailOutbox).order_by(EmailOutbox.created_at.desc()).limit(100)
    ).all()
    return render_template("admin/email_outbox.html", msgs=msgs)
