import smtplib
import ssl
import os
from ua_appointment_checker.constants import GMAIL_PASSWORD_KEY
from email.message import EmailMessage


def send_email(sender: str, recipient: str, message: str, subject: str):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        password = os.environ.get(GMAIL_PASSWORD_KEY, "")
        if not password:
            raise ValueError(
                f"No email password found. Please set {GMAIL_PASSWORD_KEY} as env variable."
            )
        server.login(sender, password)
        em = EmailMessage()
        em["From"] = sender
        em["To"] = recipient
        em["Subject"] = subject
        em.set_content(message)
        server.sendmail(sender, recipient, em.as_string())
