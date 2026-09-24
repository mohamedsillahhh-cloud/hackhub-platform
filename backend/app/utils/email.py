import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)


def _message(to: str, subject: str, body_html: str) -> MIMEMultipart:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to
    message.attach(MIMEText(body_html, "html"))
    return message


def _send_messages(recipients: List[str], subject: str, body_html: str) -> None:
    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        for recipient in recipients:
            message = _message(recipient, subject, body_html)
            server.sendmail(settings.SMTP_FROM_EMAIL, [recipient], message.as_string())


async def send_email(to: str, subject: str, body_html: str) -> bool:
    return await send_bulk_email([to], subject, body_html)


async def send_bulk_email(to_list: List[str], subject: str, body_html: str) -> bool:
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return False

    try:
        await asyncio.to_thread(_send_messages, to_list, subject, body_html)
        return True
    except (OSError, smtplib.SMTPException):
        logger.exception("Email delivery failed")
        return False
