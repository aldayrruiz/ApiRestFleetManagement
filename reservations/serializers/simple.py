from rest_framework import serializers

from reservations.models import Reservation
from users.serializers.simple import SimpleUserSerializer
from vehicles.serializers.simple import SimpleVehicleSerializer


class SimpleReservationSerializer(serializers.ModelSerializer):
    # Incidents array in user field has vehicle's pk. NOT incident's pk
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'date_stored', 'start', 'end', 'description', 'owner', 'vehicle']
