from __future__ import annotations

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SENDER_EMAIL, SENDER_PASSWORD, RESUME_PATH
from email_builder import build_email
from logger import Logger


def connect_smtp(log: Logger) -> smtplib.SMTP | None:
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        log.log("🔐 Logged in to Gmail SMTP successfully.")
        return server
    except smtplib.SMTPAuthenticationError:
        log.log("❌ Authentication failed. Use a Gmail App Password — myaccount.google.com/apppasswords")
    except Exception as e:
        log.log(f"❌ Could not connect to SMTP: {e}")
    return None


def dispatch_email(server: smtplib.SMTP, recipient: str, hr_name: str, company_name: str, design_format: str = "HR"):
    subject, html_body = build_email(hr_name, company_name, design_format)

    msg = MIMEMultipart("alternative")
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    if RESUME_PATH and os.path.exists(RESUME_PATH):
        with open(RESUME_PATH, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(RESUME_PATH)}"')
        msg.attach(part)
    elif RESUME_PATH:
        print(f"  ⚠️  Resume not found at '{RESUME_PATH}' — sending without attachment.")

    server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
