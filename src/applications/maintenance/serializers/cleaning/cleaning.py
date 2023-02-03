from rest_framework import serializers

from applications.maintenance.models import Cleaning
from applications.maintenance.serializers.cleaning.photo import SimpleCleaningPhotoSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateCleaningSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = Cleaning
        fields = ['id', 'owner', 'vehicle', 'date', 'type', 'status', 'tenant']


class SimpleCleaningSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    photos = SimpleCleaningPhotoSerializer(many=True)

    class Meta:
        model = Cleaning
        fields = ['id', 'owner', 'vehicle', 'date', 'type', 'completed', 'status',
                  'last_updated', 'date_stored', 'photos']
