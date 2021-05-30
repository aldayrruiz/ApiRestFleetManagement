from rest_framework import serializers

from applications.vehicles.models import Vehicle


class SimpleVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'date_stored']
