from rest_framework import serializers

from applications.maintenance.models import Wheels
from applications.maintenance.serializers.wheels.photo import SimpleWheelsPhotoSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateWheelsSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = Wheels
        fields = ['id', 'owner', 'vehicle', 'date', 'location', 'kilometers', 'operation',
                  'passed', 'completed', 'status', 'next_revision', 'next_kilometers', 'tenant']


class SimpleWheelsSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    photos = SimpleWheelsPhotoSerializer(many=True)

    class Meta:
        model = Wheels
        fields = ['id', 'owner', 'vehicle', 'date', 'location', 'kilometers', 'operation',
                  'passed', 'completed', 'status', 'next_revision', 'next_kilometers',
                  'last_updated', 'date_stored', 'photos']
