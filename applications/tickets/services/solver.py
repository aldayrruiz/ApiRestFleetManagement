import logging

from applications.reservations.utils import is_reservation_already_started, delete_reservation
from applications.tickets.models import TicketStatus
from utils.email.tickets import send_reservation_deleted_email, send_accepted_ticket_email, send_denied_ticket_email

logger = logging.getLogger(__name__)


def solve_ticket(ticket, new_status):
    reservation = ticket.reservation
    if is_reservation_already_started(reservation):
        logger.exception('Cannot delete a reservation which has already started: {}'.format(reservation.id))

    if new_status == TicketStatus.UNSOLVED:
        logger.exception('Cannot solve a ticket with status UNSOLVED')
    elif new_status == TicketStatus.ACCEPTED:
        send_reservation_deleted_email(reservation)
        send_accepted_ticket_email(ticket)
        ticket.delete()
        delete_reservation(reservation, new_ticket_st=TicketStatus.DENIED)
    elif new_status == TicketStatus.DENIED:
        send_denied_ticket_email(ticket)
        ticket.delete()
    else:
        logger.exception('Unsupported')
