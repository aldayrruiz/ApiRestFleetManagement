from applications.reservations.models import Reservation
from utils.dates import get_now_utc, from_naive_to_aware


class ReservationValidator:
    def __init__(self, vehicle):
        self.queryset = Reservation.objects.filter(start__gt=get_now_utc(), vehicle=vehicle)

    def is_reservation_valid(self, reservation):
        for r in self.queryset.all():
            start = from_naive_to_aware(reservation.start)
            end = from_naive_to_aware(reservation.end)
            valid = start >= r.end or end <= r.start
            if not valid:
                return False
        return True
