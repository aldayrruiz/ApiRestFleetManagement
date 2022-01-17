from utils.email.shared import send_email, create_message


# Email to ticket's owner when the ticket is accepted
def send_accepted_ticket_email(ticket):
    receiver_email = ticket.owner.email
    message = get_accepted_ticket_message(ticket=ticket)
    send_email(receiver_email=receiver_email, message=message)


def get_accepted_ticket_message(ticket):
    reservation = ticket.reservation
    vehicle = reservation.vehicle
    receiver_email = ticket.owner.email

    subject = 'Ticket aceptado'
    body = """
    El siguiente ticket ha sido aceptado:
    Título: {0}
    Descripción: {1}

    Detalles de la reserva eliminada por su ticket:
    Marca: {2}
    Modelo: {3}
    Matricula: {4}
    Fecha de recogida: {5}
    Fecha de entrega: {6}
    """.format(
        ticket.title,
        ticket.description,
        vehicle.brand,
        vehicle.model,
        vehicle.number_plate,
        reservation.start,
        reservation.end
    )

    return create_message(receiver_email=receiver_email, subject=subject, body=body)