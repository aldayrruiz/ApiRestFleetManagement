from rest_framework import serializers

from incidents.models import Incident


class CreateIncidentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    solved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Incident
        fields = ['id', 'title', 'description', 'owner', 'reservation', 'type', 'solved']
