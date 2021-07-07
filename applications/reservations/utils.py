from datetime import datetime

import pytz

from utils.email.tickets import send_accepted_ticket_email

TIMEZONE = 'UTC'


def is_reservation_already_started(reservation):
    now = _get_now_utc()
    return reservation.start < now


def is_reservation_already_ended(reservation):
    now = _get_now_utc()
    return reservation.end < now


def delete_reservation(reservation):
    tickets = reservation.tickets.all()
    for ticket in tickets:
        send_accepted_ticket_email(ticket)
    reservation.delete()


def _get_now_utc():
    timezone = pytz.timezone(TIMEZONE)
    return datetime.now().astimezone(timezone)
