from datetime import datetime

import pytz

from utils.email.tickets import send_accepted_ticket_email

TIMEZONE = 'UTC'


def is_reservation_already_started(reservation):
    timezone = pytz.timezone(TIMEZONE)
    now = datetime.now().astimezone(timezone)

    return reservation.start < now


def delete_reservation(reservation):
    tickets = reservation.tickets
    for ticket in tickets:
        send_accepted_ticket_email(ticket)
    reservation.delete()
