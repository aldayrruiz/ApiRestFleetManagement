import logging

from rest_framework.exceptions import ValidationError

from applications.reservations.exceptions.already_started import ReservationAlreadyStarted
from applications.reservations.services.destroyer import delete_reservation
from applications.reservations.services.timer import reservation_already_started
from applications.tickets.models import TicketStatus
from utils.email.tickets.accepted import send_accepted_ticket_email
from utils.email.tickets.denied import send_denied_ticket_email
from utils.email.tickets.reservation_deleted import send_reservation_deleted_email

logger = logging.getLogger(__name__)


def solve_ticket(ticket, status):
    reservation = ticket.reservation
    if reservation_already_started(reservation):
        raise ReservationAlreadyStarted()

    if status == TicketStatus.UNSOLVED:
        logger.exception('Cannot solve a ticket with status UNSOLVED')
    elif status == TicketStatus.ACCEPTED:
        send_reservation_deleted_email(reservation)
        send_accepted_ticket_email(ticket)
        # Update ticket status
        ticket.status = status
        ticket.save()
        # Delete reservation and send emails to users which have a ticket into reservation that their ticket was denied.
        reservation.delete()
    elif status == TicketStatus.DENIED:
        # Update ticket status
        ticket.status = status
        ticket.save()
        send_denied_ticket_email(ticket)
    else:
        raise ValidationError('Unknown ticket status')
