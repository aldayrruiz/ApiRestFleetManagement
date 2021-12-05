from rest_framework import serializers

from applications.reservations.serializers.validator import validate
from utils.dates import WeekDay


class RecurrentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    startReservationTime = serializers.DateTimeField(required=True)
    endReservationTime = serializers.DateTimeField(required=True)
    weekdays = serializers.ListField(child=serializers.ChoiceField(choices=WeekDay.choices, required=True),
                                     allow_empty=False)
    startReservations = serializers.DateTimeField(required=True)
    endReservations = serializers.DateTimeField(required=True)
    vehicles = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)


class CreateByDate(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    description = serializers.CharField(style={'base_template': 'textarea.html'})
    start = serializers.DateTimeField(required=True)
    end = serializers.DateTimeField(required=True)
    vehicles = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)

    def validate(self, data):
        validate(data)
        return data
