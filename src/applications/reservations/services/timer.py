import logging

from rest_framework.exceptions import ValidationError

from utils.dates import get_now_utc

logger = logging.getLogger(__name__)


def reservation_already_started(reservation):
    now = get_now_utc()
    return reservation.start < now


def reservation_already_ended(reservation):
    now = get_now_utc()
    return reservation.end < now


def raise_error_if_reservation_has_not_ended(reservation):
    already_ended = reservation_already_ended(reservation)
    if not already_ended:
        raise ValidationError(f'Reservation has not ended.')
