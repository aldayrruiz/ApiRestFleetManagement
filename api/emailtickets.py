import smtplib
import ssl
import json


def send_emails(admins, reservation, ticket):
    with open('api/emailconfig.json') as json_file:
        data = json.load(json_file)

    port = data['port']
    smtp_server = data['smtp_server']
    sender = data['sender']
    password = data['password']

    vehicle_desired = reservation.vehicle
    requester = ticket.owner

    # TODO: Change email message for html one.
    message = """\
    Subject: Se ha presentado un ticket.
    
    El usuario {0} ha presentado un ticket para el vehiculo {1} con el siguiente motivo:
    {2}
    El motivo del propietario de la reserva es el siguiente:
    {3}"""\
        .format(
        requester.username,
        vehicle_desired.name,
        ticket.description,
        reservation.description
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, password)
        # Send emails to admins
        for admin in admins:
            server.sendmail(sender, admin.email, message)
