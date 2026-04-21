from __future__ import annotations
import smtplib
from email.message import EmailMessage
from flask import current_app

class EmailDeliveryError(Exception):
    pass

def send_email(*, to_email: str, subject: str, body: str) -> None:
    cfg = current_app.config

    host = cfg.get("SMTP_HOST")
    port = cfg.get("SMTP_PORT", 587)
    username = cfg.get("SMTP_USERNAME")
    password = cfg.get("SMTP_PASSWORD")
    sender = cfg.get("SMTP_SENDER")

    if not all([host, username, password, sender]):
        raise EmailDeliveryError("SMTP is not configured.")
    
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
    except Exception as e:
        raise EmailDeliveryError(str(e)) from e
