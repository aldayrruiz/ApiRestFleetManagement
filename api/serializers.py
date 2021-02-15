from rest_framework import serializers
from .models import *


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'date_stored', 'days_to_use', 'available', 'type']
        depth = 1


# Allows to not define explicitly id and date_store.
class CreateVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['name', 'days_to_use', 'available', 'type']

    def validate(self, data):
        """
        Check days to use is not negative.
        """
        if data['days_to_use'] <= 0:
            raise serializers.ValidationError("Vehicle's days to use must be > 0")
        return data


class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id', 'name']


