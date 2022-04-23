from utils.email.shared import send_email, create_message


# Email to ticket's owner when the ticket is denied
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
