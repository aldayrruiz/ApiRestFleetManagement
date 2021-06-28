from rest_framework import serializers

from applications.vehicles.models import Vehicle


class SimpleVehicleSerializer(serializers.ModelSerializer):

    gps_device = serializers.ReadOnlyField(source='gps_device.imei')

    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'gps_device', 'date_stored', 'is_disabled']
