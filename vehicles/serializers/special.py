# Include reservations of vehicle. Perfect a single vehicle.
from rest_framework import serializers

from reservations.serializers.simple import SimpleReservationSerializer
from vehicles.models import Vehicle


class DetailedVehicleSerializer(serializers.ModelSerializer):
    reservations = SimpleReservationSerializer(many=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'date_stored', 'reservations']
