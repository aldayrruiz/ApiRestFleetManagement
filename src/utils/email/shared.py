import logging
import smtplib
import ssl
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections.abc import Sequence
from typing import Union
from decouple import config

emails = config('EMAILS_STATUS')
smtp_port = config('SMTP_PORT')
smtp_server = config('SMTP_SERVER')
sender_email = config('SENDER_EMAIL')
sender_password = config('SENDER_PASSWORD')

logger = logging.getLogger(__name__)


def are_emails_enabled():
    return emails in ['Enabled', 'enabled', 'True', 'true']


emails_enabled = are_emails_enabled()

if not (smtp_port and smtp_server and sender_email and sender_password):
    logger.critical('Email configuration was not found (see .env file).')

if not emails_enabled:
    logger.critical('Emails are disabled (see .env file). Ignore it, if you are in developer mode.')


def create_message(receiver_email, subject, body):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = formataddr(('BLUE Drivers', sender_email))
    message["To"] = receiver_email
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails

    message.attach(MIMEText(body, "plain"))
    return message.as_string()


def send_email(receiver_email, message):
    if not emails_enabled:
        return

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)


class EmailSender:
    def __init__(self, to_addrs: Union[str, Sequence[str]], subject: str):
        self.to_addrs = to_addrs
        self.message = MIMEMultipart('alternative')
        self.message["From"] = formataddr(('BLUE Drivers', sender_email))
        self.message["To"] = self.to_addrs
        self.message["Subject"] = subject

    def attach_html(self, html):
        self.message.attach(MIMEText(html, 'html'))

    def attach_plain(self, plain):
        self.message.attach(MIMEText(plain, 'plain'))

    def send(self):
        if not emails_enabled:
            return

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg=self.message)
