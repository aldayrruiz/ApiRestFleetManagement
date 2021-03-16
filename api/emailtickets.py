import smtplib
import ssl
import json


def send_email(reservation, description):

    with open('api/emailconfig.json') as json_file:
        data = json.load(json_file)

    port = data['port']
    smtp_server = data['smtp_server']
    sender = data['sender']
    password = data['password']

    receiver = reservation.user.email

    message = """\
    Subject: Has recibido un ticket

    Alguien mas quiere el vehiculo {0} que has reservado el dia {1}""".format(reservation.vehicle.name, reservation.start)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message)
