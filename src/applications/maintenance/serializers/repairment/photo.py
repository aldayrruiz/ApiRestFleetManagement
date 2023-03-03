from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.maintenance.models import RepairmentPhoto
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateRepairmentPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = RepairmentPhoto
        fields = ['id', 'owner', 'repairment', 'photo', 'tenant']


class SimpleRepairmentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairmentPhoto
        fields = ['id', 'photo']