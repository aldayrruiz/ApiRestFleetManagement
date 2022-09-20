from rest_framework import serializers

from applications.incidents.models import Incident


class SolveIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['solver_message']
