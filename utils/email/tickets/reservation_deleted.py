from utils.email.shared import send_email, create_message


# Email to reservation's owner when his reservation is deleted by a ticket.
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
