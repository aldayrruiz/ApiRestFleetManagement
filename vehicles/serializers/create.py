from rest_framework import serializers

from vehicles.models import Vehicle


class CreateOrUpdateVehicleSerializer(serializers.ModelSerializer):
    # type = serializers.CharField(max_length=50, source='type.name')

    class Meta:
        model = Vehicle
        fields = ['id', 'name']
