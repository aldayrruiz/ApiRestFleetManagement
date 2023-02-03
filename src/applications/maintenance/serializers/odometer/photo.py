from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.maintenance.models import OdometerPhoto
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateOdometerPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = OdometerPhoto
        fields = ['id', 'owner', 'odometer', 'photo', 'tenant']


class SimpleOdometerPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdometerPhoto
        fields = ['id', 'photo']
