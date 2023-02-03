from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.maintenance.models import CleaningPhoto
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateCleaningPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = CleaningPhoto
        fields = ['id', 'owner', 'cleaning', 'photo', 'tenant']


class SimpleCleaningPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CleaningPhoto
        fields = ['id', 'photo']