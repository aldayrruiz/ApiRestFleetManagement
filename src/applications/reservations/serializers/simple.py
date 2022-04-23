from rest_framework import serializers

from applications.reservations.models import Reservation, Recurrent
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer


class SimpleRecurrentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurrent
        fields = ['id', 'weekdays', 'since', 'until']


class SimpleReservationSerializer(serializers.ModelSerializer):
    # Incidents array in user field has vehicle's pk. NOT incident's pk
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    recurrent = SimpleRecurrentSerializer()

    class Meta:
        model = Reservation
        fields = [
            'id',
            'title',
            'date_stored',
            'start',
            'end',
            'description',
            'owner',
            'vehicle',
            'is_cancelled',
            'is_recurrent',
            'recurrent'
        ]
