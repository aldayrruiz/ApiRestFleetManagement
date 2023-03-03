from rest_framework import serializers

from applications.maintenance.models import OdometerCard
from shared.serializer.current_tenant import CurrentTenantDefault


class OdometerCardSerializer(serializers.ModelSerializer):
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = OdometerCard
        fields = ['id', 'km_period', 'tenant']
