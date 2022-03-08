from rest_framework import serializers

from applications.incidents.models import Incident
from drf_extra_fields.fields import Base64ImageField


class CreateIncidentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    solved = serializers.BooleanField(read_only=True)
    photo = Base64ImageField(required=False)

    class Meta:
        model = Incident
        fields = ['id', 'description', 'owner', 'reservation', 'type', 'solved', 'photo']
