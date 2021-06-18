from rest_framework import serializers

from applications.vehicles.models import Vehicle


class CreateOrUpdateVehicleSerializer(serializers.ModelSerializer):
    gps_device = serializers.ReadOnlyField(source='gps_device.imei')

    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'is_disabled', 'gps_device']
