from rest_framework import serializers

from vehicles.models import Vehicle


class SimpleVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'date_stored']
