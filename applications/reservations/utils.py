import logging
from datetime import datetime

import pytz

from applications.tickets.models import TicketStatus
from utils.email.tickets import send_accepted_ticket_email, send_denied_ticket_email

TIMEZONE = 'UTC'

logger = logging.getLogger(__name__)


def is_reservation_already_started(reservation):
    now = _get_now_utc()
    return reservation.start < now


def is_reservation_already_ended(reservation):
    now = _get_now_utc()
    return reservation.end < now


def delete_reservation(reservation, new_ticket_st=TicketStatus.DENIED):
    """
    Delete reservation and send email accepting or denying ticket depending on new_ticket_st to ticket owners.
    It does not send email of reservation deleted to owner.

    :param reservation: Reservation to delete
    :param new_ticket_st: Status to solve all reservation's tickets
    :return: None or Raise a exception if new_ticket_st not in [ACCEPTED, DENIED]
    """

    if is_reservation_already_started(reservation):
        logger.exception('Cannot delete a reservation which has already started: {}'.format(reservation.id))

    if new_ticket_st is TicketStatus.ACCEPTED:
        send_email = send_accepted_ticket_email
    elif new_ticket_st is TicketStatus.DENIED:
        send_email = send_denied_ticket_email
    else:
        logger.exception('Cannot delete a reservation and solve their ticket with a status: {}'.format(new_ticket_st))
        return

    tickets = reservation.tickets.all()
    for ticket in tickets:
        send_email(ticket)
    reservation.delete()


def _get_now_utc():
    timezone = pytz.timezone(TIMEZONE)
    return datetime.now().astimezone(timezone)
