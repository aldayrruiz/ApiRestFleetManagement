from rest_framework import serializers

from applications.maintenance.models import CleaningCard
from shared.serializer.current_tenant import CurrentTenantDefault


class CleaningCardSerializer(serializers.ModelSerializer):
    tenant = serializers.HiddenField(default=CurrentTenantDefault())

    class Meta:
        model = CleaningCard
        fields = ['id', 'vehicle', 'date_period', 'tenant']
