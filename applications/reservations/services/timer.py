import logging

from utils.dates import get_now_utc

logger = logging.getLogger(__name__)


def reservation_already_started(reservation):
    now = get_now_utc()
    return reservation.start < now


def reservation_already_ended(reservation):
    now = get_now_utc()
    return reservation.end < now
