from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *
from django.contrib.auth import get_user_model


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'date_stored', 'days_to_use', 'available', 'type']
        depth = 1


class CreateVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['name', 'days_to_use', 'available', 'type']

    def validate(self, data):
        """
        Check days to use is not negative.
        """
        if data['days_to_use'] <= 0:
            raise serializers.ValidationError("Vehicle's days to use must be > 0")
        return data


class VehicleTypeSerializer(serializers.ModelSerializer):
    vehicles = VehicleSerializer(many=True)

    class Meta:
        model = VehicleType
        fields = ['id', 'name', 'vehicles']


class CreateVehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['name']


class CreateReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['start', 'end', 'user', 'vehicle']

    def validate(self, data):
        """
        Check reservation date is ok
        """
        if data['start'] > data['end']:
            raise serializers.ValidationError("Reservation's start date must be before of end date")
        # TODO: Check if there is a reservation of this vehicle at the same datetime already.
        # TODO: A reservation must be >= to date.now
        return data


class ReservationSerializer(serializers.ModelSerializer):
    # Incidents array in user field has vehicle's pk. NOT incident's pk
    user = serializers.ReadOnlyField(source='user.username')
    vehicle = VehicleSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'start', 'end', 'user', 'vehicle']


class UserSerializer(serializers.ModelSerializer):
    reservations = serializers.PrimaryKeyRelatedField(many=True, queryset=Reservation.objects.all())
    # reservations = ReservationSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'date_joined', 'reservations']
