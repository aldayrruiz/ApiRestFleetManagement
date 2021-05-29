from rest_framework import serializers

from reservations.serializers.simple import SimpleReservationSerializer
from vehicles.models import Vehicle


class DetailedVehicleSerializer(serializers.ModelSerializer):
    reservations = SimpleReservationSerializer(many=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'date_stored', 'reservations']
