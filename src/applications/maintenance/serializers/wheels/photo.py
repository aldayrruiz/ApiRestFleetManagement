from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.maintenance.models import WheelsPhoto
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateWheelsPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = WheelsPhoto
        fields = ['id', 'owner', 'wheels', 'photo', 'tenant']


class SimpleWheelsPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WheelsPhoto
        fields = ['id', 'photo']