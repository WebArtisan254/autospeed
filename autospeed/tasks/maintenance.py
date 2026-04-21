from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from flask import current_app
from ..models import db, User_Token, EmailOutbox

def cleanup_expired_tokens_and_stale_email() -> None:
    now = datetime.now(timezone.utc)

    expired = db.session.execute(
        delete(User_Token).where(User_Token.expires_at < now)
    ).rowcount

    stale_cutoff = now - timedelta(days=2)
    stale = db.session.scalars(
        select(EmailOutbox).where(
            EmailOutbox.status == "failed",
            EmailOutbox.created_at < stale_cutoff,
        )
    ).all()

    for msg in stale:
        current_app.logger.warning(
            "Stale email outbox record %s to %s: %s",
            msg.id,
            msg.to_email,
            msg.last_error,
        )

    db.session.commit()

    current_app.logger.info(
        "Maintenance run: removed %s expired tokens, found %s stale email records",
        expired,
        len(stale),
    )
