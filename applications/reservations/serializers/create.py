from rest_framework import serializers

from applications.reservations.models import Reservation


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

        # TODO: Reservation must be a minimum of 1h

        # Check reservation's start date < end date
        if data['start'] > data['end']:
            raise serializers.ValidationError("Reservation's start date must be before of end date")

        reservations = Reservation.objects.filter(vehicle__id=data['vehicle'].id, is_cancelled=False)

        for reservation in reservations:
            if not is_reservation_valid(data, reservation):
                raise serializers.ValidationError("A reservation occurs at the same time.")
        return data
