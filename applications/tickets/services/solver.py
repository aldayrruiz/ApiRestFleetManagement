from applications.reservations.utils import is_reservation_already_started
from applications.tickets.models import TicketStatus
from utils.email.emailtickets import send_accepted_ticket_email, send_denied_ticket_email, \
    send_reservation_deleted_email


def solve_ticket(ticket, new_status):
    reservation = ticket.reservation
    if is_reservation_already_started(reservation):
        return "Can't solve a reservation already started"

    if new_status == TicketStatus.UNSOLVED:
        return "Can't solve a ticket to unsolved status"
    elif new_status == TicketStatus.ACCEPTED:
        send_reservation_deleted_email(reservation)
        send_accepted_ticket_email(ticket)
        reservation.delete()
    elif new_status == TicketStatus.DENIED:
        send_denied_ticket_email(ticket)
    else:
        return "Unsupported status"

    ticket.status = new_status
