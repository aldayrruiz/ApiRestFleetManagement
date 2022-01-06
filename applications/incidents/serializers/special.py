from rest_framework import serializers


class SolveIncidentSerializer(serializers.Serializer):
    email = serializers.BooleanField(default=True)
    solved = serializers.BooleanField(default=True)
