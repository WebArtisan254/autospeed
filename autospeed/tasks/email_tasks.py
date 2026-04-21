from __future__ import annotations
from datetime import datetime, timezone
from flask import current_app
from ..emailing import send_email, EmailDeliveryError
from ..models import db, EmailOutbox
from .telemetry import TaskTimer


def deliver_outbox_email(*, outbox_id: int) -> None:
    with TaskTimer("deliver_outbox_email", str(outbox_id)):
        if not isinstance(outbox_id, int):
            current_app.logger.error("Invalid outbox_id payload: %r", outbox_id)
            return

        msg = db.session.get(EmailOutbox, outbox_id)
        if msg is None:
            current_app.logger.warning("Outbox id=%s not found", outbox_id)
            return

        if msg.status == "sent" and msg.sent_at is not None:
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
            db.session.rollback()
            msg = db.session.get(EmailOutbox, outbox_id)
            if msg is not None:
                msg.status = "failed"
                msg.last_error = str(e)
                db.session.commit()
            current_app.logger.exception("Outbox send failed id=%s", outbox_id)
            raise
        except Exception as e:
            db.session.rollback()
            msg = db.session.get(EmailOutbox, outbox_id)
            if msg is not None:
                msg.status = "failed"
                msg.last_error = str(e)
                db.session.commit()
            current_app.logger.exception("Outbox send errored id=%s", outbox_id)
            raise

        msg = db.session.get(EmailOutbox, outbox_id)
        if msg is not None:
            msg.status = "sent"
            msg.sent_at = datetime.now(timezone.utc)
            msg.last_error = None
            db.session.commit()
