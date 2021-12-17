from rest_framework import serializers

from applications.reservations.models import Reservation, Recurrent
from applications.reservations.serializers.validator import validate


def is_reservation_valid(new_reservation, reservation):
    if new_reservation['start'] >= reservation.end or new_reservation['end'] <= reservation.start:
        return True
    return False


class CreateReservationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'date_stored', 'start', 'end', 'description', 'owner', 'vehicle', 'is_cancelled']

    def validate(self, data):
        validate(data)

        reservations = Reservation.objects.filter(vehicle__id=data['vehicle'].id, is_cancelled=False)

        for reservation in reservations:
            if not is_reservation_valid(data, reservation):
                raise serializers.ValidationError("Una reserva ocurre al mismo tiempo")
        return data


class CreateRecurrentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Recurrent
        fields = ['id', 'owner', 'weekdays', 'since', 'until']