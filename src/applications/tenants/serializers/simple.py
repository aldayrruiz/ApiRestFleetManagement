from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from applications.tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'diet']


class CreateTenantSerializer(serializers.ModelSerializer):
    logo = Base64ImageField(required=False)

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'diet', 'logo']
