from utils.email.shared import send_email, create_message


# Email to the admin when a ticket is created
def send_created_ticket_email(admin, ticket):
    receiver_email = admin.email
    message = get_ticket_created_message(receiver_email=receiver_email, ticket=ticket)
    send_email(receiver_email=receiver_email, message=message)


def get_ticket_created_message(receiver_email, ticket):
    owner = ticket.owner.fullname
    reservation = ticket.reservation
    vehicle = reservation.vehicle

    subject = 'Un ticket ha sido creado'
    body = """
    El usuario {0} ha presentado un ticket contra la reserva:
    Marca: {1}
    Modelo: {2}
    Matricula: {3}
    Descripción: {4}
    Fecha de recogida: {5} 
    Fecha de entrega: {6}

    El motivo por el cual se ha presentado el ticket es:
    {7}
    """.format(
        owner,
        vehicle.brand,
        vehicle.model,
        vehicle.number_plate,
        reservation.description,
        reservation.start,
        reservation.end,
        ticket.description
    )

    return create_message(receiver_email=receiver_email, subject=subject, body=body)

