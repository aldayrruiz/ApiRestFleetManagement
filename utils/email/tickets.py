from utils.email.shared import send_email, create_message


# Send an email to the admin when a ticket is created
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


# Send an email to ticket's owner when the ticket is denied
def send_denied_ticket_email(ticket):
    receiver_email = ticket.owner.email
    message = get_denied_ticket_message(ticket)
    send_email(receiver_email=receiver_email, message=message)


def get_denied_ticket_message(ticket):
    receiver_email = ticket.owner.email
    subject = 'Ticket denegado'
    body = """
    El siguiente ticket ha sido denegado:
    Título: {0}
    Descripción: {1}
    """.format(ticket.title, ticket.description)

    return create_message(receiver_email=receiver_email, subject=subject, body=body)


# Send an email to ticket's owner when the ticket is accepted
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


# Send an email to reservation's owner when his reservation is deleted by a ticket.
def send_reservation_deleted_email(reservation):
    receiver_email = reservation.owner.email
    message = get_reservation_deleted_message(reservation=reservation)
    send_email(receiver_email=receiver_email, message=message)


def get_reservation_deleted_message(reservation):
    vehicle = reservation.vehicle
    receiver_email = reservation.owner.email

    subject = 'Reserva eliminada'
    body = """
    Su reserva ha sido eliminada porque alguien tenía una mayor prioridad.
    Los detalles de su reserva eran:
    Título: {0}
    Descripción: {1}
    Marca: {2}
    Modelo: {3}
    Matricula: {4}
    Fecha de recogida: {5}
    Fecha de entrega: {6}
        """.format(
        reservation.title,
        reservation.description,
        vehicle.brand,
        vehicle.model,
        vehicle.number_plate,
        reservation.start,
        reservation.end
    )

    return create_message(receiver_email=receiver_email, subject=subject, body=body)
