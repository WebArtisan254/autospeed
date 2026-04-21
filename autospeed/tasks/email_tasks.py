from __future__ import annotations
from flask import current_app
from ..emailing import send_email, EmailDeliveryError
from ..jobs import get_queue
from sqlalchemy import select
from ..models import db, EmailOutbox
from datetime import datetime

q = get_queue()
q.enqueue(
    "autospeed.tasks.email_tasks.send_password_reset_email",
    to_email=user.email,
    reset_link=reset_link,
    retry=3,
)

def send_password_reset_email(*, to_email: str, reset_link: str) -> None:
    subject = "Reset your password"
    body = (
        "You requested a password reset.\n\n"
        f"Reset your password using this link:\n{reset_link}\n\n"
        "If you did not request this, you can ignore this email."
    )

    current_app.logger.info("Sending password reset email to %s", to_email)
    send_email(to_email=to_email, subject=subject, body=body)

def deliver_outbox_email(*, outbox_id: int) -> None:
    msg = db.session.get(EmailOutbox, outbox_id)
    if msg is None or msg.status == "sent":
        return

    if msg.status != "pending":
        return

    msg.status = "sending"
    msg.attempts += 1
    msg.last_error = None
    db.session.commit()

    try:
        send_email(to_email=msg.to_email, subject=msg.subject, body=msg.body)
    except EmailDeliveryError as e:
        msg = db.session.get(EmailOutbox, outbox_id)
        if msg is not None:
            msg.status = "failed"
            msg.last_error = str(e)
            db.session.commit()
        raise

    msg = db.session.get(EmailOutbox, outbox_id)
    if msg is not None:
        msg.status = "sent"
        msg.sent_at = datetime.utcnow()
        msg.last_error = None
        db.session.commit()