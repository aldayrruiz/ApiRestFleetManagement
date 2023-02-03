from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.maintenance.models import ItvPhoto
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateItvPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = ItvPhoto
        fields = ['id', 'owner', 'itv', 'photo', 'tenant']


class SimpleItvPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItvPhoto
        fields = ['id', 'photo']
