from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.maintenance.models import RevisionPhoto
from shared.serializer.current_tenant import CurrentTenantDefault


class CreateRevisionPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tenant = serializers.HiddenField(default=CurrentTenantDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = RevisionPhoto
        fields = ['id', 'owner', 'revision', 'photo', 'tenant']


class SimpleRevisionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionPhoto
        fields = ['id', 'photo']