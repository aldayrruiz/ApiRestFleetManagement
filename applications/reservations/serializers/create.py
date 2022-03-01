from rest_framework import serializers

from applications.reservations.exceptions.already_posses_reservation_at_the_same_time import \
    YouAlreadyPossesOtherReservationAtSameTime
from applications.reservations.exceptions.another_person_posses_this_vehicle import AnotherPersonPossesThisVehicle
from applications.reservations.models import Reservation, Recurrent
from applications.reservations.serializers.validator import validate_reservation_dates
from utils.dates import get_now_utc


def is_reservation_valid(new_reservation, reservation):
    if new_reservation['start'] >= reservation.end or new_reservation['end'] <= reservation.start:
        return True
    return False


class CreateReservationSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'date_stored', 'start', 'end', 'description', 'owner', 'vehicle']

    def validate(self, data):
        validate_reservation_dates(data)

        requester = data['owner']
        future_reservations = Reservation.objects.exclude(end__lt=get_now_utc())
        vehicle_reservations = future_reservations.filter(vehicle__id=data['vehicle'].id)
        own_reservations = future_reservations.filter(owner_id=requester.id)
        possible_problematic_reservations = (vehicle_reservations | own_reservations).distinct()

        for reservation in possible_problematic_reservations:
            if not is_reservation_valid(data, reservation):
                if reservation.owner == requester:
                    raise YouAlreadyPossesOtherReservationAtSameTime()
                raise AnotherPersonPossesThisVehicle()
        return data


class CreateRecurrentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Recurrent
        fields = ['id', 'owner', 'weekdays', 'since', 'until']
