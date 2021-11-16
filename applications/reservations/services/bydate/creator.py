from operator import itemgetter

from applications.allowed_vehicles.services.queryset import get_allowed_vehicles_queryset
from applications.reservations.models import Reservation
from applications.reservations.services.validator import ReservationValidator
from utils.dates import from_naive_to_aware


class ReservationByDateCreator:
    def __init__(self, title, description, start, end):
        self.title = title
        self.description = description
        self.start = from_naive_to_aware(start)
        self.end = from_naive_to_aware(end)

    def create(self, requester):
        """
        Return reservation created. Otherwise, None is returned.
        """
        vehicles = get_allowed_vehicles_queryset(requester)
        for vehicle in vehicles:
            possible_reservation = self.__get_reservation__(requester, vehicle)
            validator = ReservationValidator(vehicle)
            is_valid = validator.is_reservation_valid(possible_reservation)
            if is_valid:
                possible_reservation.save()
                return possible_reservation
        return None

    def __get_reservation__(self, requester, vehicle):
        reservation = Reservation(
            title=self.title,
            description=self.description,
            start=self.start,
            end=self.end,
            vehicle=vehicle,
            owner=requester,
            tenant=requester.tenant
        )
        return reservation

    @staticmethod
    def from_serializer(serializer):
        # Just taking all variables from body request
        (
            title,
            description,
            start,
            end,
        ) = itemgetter('title',
                       'description',
                       'start',
                       'end')(serializer.validated_data)

        return ReservationByDateCreator(title, description, start, end)
