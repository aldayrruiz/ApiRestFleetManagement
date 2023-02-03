from rest_framework import serializers

from applications.maintenance.models import Itv
from applications.maintenance.serializers.itv.photo import SimpleItvPhotoSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateItvSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = Itv
        fields = ['id', 'owner', 'vehicle', 'date', 'place', 'passed', 'next_revision', 'completed', 'status',
                  'tenant']


class SimpleItvSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    photos = SimpleItvPhotoSerializer(many=True)

    class Meta:
        model = Itv
        fields = ['id', 'owner', 'vehicle', 'date', 'place', 'passed', 'next_revision', 'completed', 'status',
                  'last_updated', 'date_stored', 'photos']
