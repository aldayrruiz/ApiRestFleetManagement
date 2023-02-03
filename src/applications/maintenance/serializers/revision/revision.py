from rest_framework import serializers

from applications.maintenance.models import Revision
from applications.maintenance.serializers.revision.photo import SimpleRevisionPhotoSerializer
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateRevisionSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = Revision
        fields = ['id', 'owner', 'vehicle', 'date', 'kilometers', 'motive', 'garage', 'next_revision',
                  'next_kilometers', 'completed', 'status', 'tenant']


class SimpleRevisionSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()
    photos = SimpleRevisionPhotoSerializer(many=True)

    class Meta:
        model = Revision
        fields = ['id', 'owner', 'vehicle', 'date', 'kilometers', 'motive', 'garage', 'next_revision',
                  'next_kilometers', 'completed', 'status', 'last_updated', 'date_stored', 'photos']
