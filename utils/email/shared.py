import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml


def read_config():
    with open('utils/email/config.yaml') as config_file:
        data = yaml.load(config_file, Loader=yaml.FullLoader)
    return data


def create_message(sender_email, receiver_email, subject, body):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    message.attach(MIMEText(body, "plain"))
    return message.as_string()


def send_email(email_config, receiver_email, message):
    smtp_port, smtp_server, sender_email, sender_password = email_config.values()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)
