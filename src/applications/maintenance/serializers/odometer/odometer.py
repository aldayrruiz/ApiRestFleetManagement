from rest_framework import serializers

from applications.maintenance.models import Odometer
from applications.maintenance.serializers.odometer.photo import SimpleOdometerPhotoSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateOdometerSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = Odometer
        fields = ['id', 'owner', 'vehicle', 'date', 'kilometers', 'completed', 'tenant']


class SimpleOdometerSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    photos = SimpleOdometerPhotoSerializer(many=True)

    class Meta:
        model = Odometer
        fields = ['id', 'owner', 'vehicle', 'date', 'kilometers', 'completed', 'status', 'last_updated', 'date_stored', 'photos']
