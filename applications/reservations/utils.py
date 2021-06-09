from datetime import datetime

import pytz

TIMEZONE = 'UTC'


def is_reservation_already_started(reservation):
    timezone = pytz.timezone(TIMEZONE)
    now = datetime.now().astimezone(timezone)

    return reservation.start < now
