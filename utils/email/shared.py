import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from decouple import config

smtp_port = config('SMTP_PORT')
smtp_server = config('SMTP_SERVER')
sender_email = config('SENDER_EMAIL')
sender_password = config('SENDER_PASSWORD')

logger = logging.getLogger(__name__)


if not (smtp_port and smtp_server and sender_email and sender_password):
    logger.critical('Email configuration was not found (see .env file).')


def create_message(receiver_email, subject, body):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    message.attach(MIMEText(body, "plain"))
    return message.as_string()


def send_email(receiver_email, message):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
