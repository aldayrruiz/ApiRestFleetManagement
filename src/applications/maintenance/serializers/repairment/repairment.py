from rest_framework import serializers

from applications.maintenance.models import Repairment
from applications.maintenance.serializers.repairment.photo import SimpleRepairmentPhotoSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateRepairmentSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = Repairment
        fields = ['id', 'owner', 'vehicle', 'date', 'kilometers', 'location', 'description',
                  'tenant']


class SimpleRepairmentSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    photos = SimpleRepairmentPhotoSerializer(many=True)

    class Meta:
        model = Repairment
        fields = ['id', 'owner', 'vehicle', 'date', 'kilometers', 'location', 'description',
                  'last_updated', 'date_stored', 'photos']
