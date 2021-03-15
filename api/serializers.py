from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

DELAY = 1


def is_reservation_valid(new_reservation, reservation):
    if new_reservation['start'] >= reservation.end or new_reservation['end'] <= reservation.start:
        return True
    return False


class CreateReservationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Reservation
        fields = ['id', 'start', 'end', 'user', 'vehicle']

    def validate(self, data):

        # Check reservation's start date < end date
        if data['start'] > data['end']:
            raise serializers.ValidationError("Reservation's start date must be before of end date")

        reservations = Reservation.objects.filter(vehicle__id=data['vehicle'].id)

        for reservation in reservations:
            if not is_reservation_valid(data, reservation):
                raise serializers.ValidationError("A reservation occurs at the same time.")
        return data


class ReservationSerializer(serializers.ModelSerializer):
    # Incidents array in user field has vehicle's pk. NOT incident's pk
    user = serializers.ReadOnlyField(source='user.username')
    vehicle = serializers.ReadOnlyField(source='vehicle.name')

    class Meta:
        model = Reservation
        fields = ['id', 'start', 'end', 'user', 'vehicle']


class UserSerializer(serializers.ModelSerializer):
    # reservations = serializers.PrimaryKeyRelatedField(many=True, queryset=Reservation.objects.all())
    # reservations = ReservationSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'date_joined']


class VehicleSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=50, source='type.name')
    reservations = ReservationSerializer(many=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'type', 'reservations']


class VehicleTypeSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True)

    class Meta:
        model = VehicleType
        fields = ['id', 'name', 'vehicles']