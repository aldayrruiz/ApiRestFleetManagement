from applications.reservations.services.queryset import get_future_reservations, get_future_reservations_of
from utils.dates import from_naive_to_aware


class ReservationValidator:
    def __init__(self, vehicle, owner):
        self.queryset = get_future_reservations().filter(vehicle=vehicle) | get_future_reservations_of(owner)

    def is_reservation_valid(self, reservation):
        for r in self.queryset.all():
            start = from_naive_to_aware(reservation.start)
            end = from_naive_to_aware(reservation.end)
            valid = start >= r.end or end <= r.start
            if not valid:
                return False
        return True
