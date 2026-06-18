import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from app.core.config import settings


async def send_email(to: str, subject: str, body_html: str) -> bool:
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to

    part = MIMEText(body_html, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, [to], message.as_string())
        return True
    except Exception:
        return False


async def send_bulk_email(to_list: List[str], subject: str, body_html: str) -> bool:
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL

    part = MIMEText(body_html, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            for recipient in to_list:
                message["To"] = recipient
                server.sendmail(settings.SMTP_FROM_EMAIL, [recipient], message.as_string())
        return True
    except Exception:
        return False
