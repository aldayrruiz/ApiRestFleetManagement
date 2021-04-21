from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

DELAY = 1


def is_reservation_valid(new_reservation, reservation):
    if new_reservation['start'] >= reservation.end or new_reservation['end'] <= reservation.start:
        return True
    return False


"""
SimpleXSerializer: This serializer must be used to retrieve, list values (User, Vehicle, etc.)
    - Dependencies with other values are serialized with its SimpleSerializer.

CreateXSerializer: This serializer must be used to update, create values (User, Vehicle, etc.)
    - Dependencies with other values are serialized with its ids.
"""


class SimpleFleetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fleet
        fields = ['id', 'name']


class SimpleVehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id', 'name']


# NOT include reservations of vehicle. Perfect for many get vehicles.
class SimpleVehicleSerializer(serializers.ModelSerializer):
    type = SimpleVehicleTypeSerializer()
    fleet = SimpleFleetSerializer()

    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'date_stored', 'type', 'fleet']


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username', 'date_joined']


class SimpleReservationSerializer(serializers.ModelSerializer):
    # Incidents array in user field has vehicle's pk. NOT incident's pk
    owner = SimpleUserSerializer()
    vehicle = SimpleVehicleSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'date_stored', 'start', 'end', 'description', 'owner', 'vehicle']


class SimpleIncidentSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer
    reservation = SimpleReservationSerializer()

    class Meta:
        model = Incident
        fields = ['id', 'title', 'date_stored', 'description', 'owner', 'reservation', 'type']


# Use as single or many tickets
class SimpleTicketSerializer(serializers.ModelSerializer):
    reservation = SimpleReservationSerializer()
    owner = SimpleUserSerializer()

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'date_stored', 'description', 'reservation', 'owner', 'status']


class CreateVehicleSerializer(serializers.ModelSerializer):
    type = serializers.CharField(max_length=50, source='type.name')

    class Meta:
        model = Vehicle
        # Fleet must be taken of admin fleet
        fields = ['id', 'name', 'type']


class CreateReservationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Reservation
        fields = ['id', 'title', 'date_stored', 'start', 'end', 'description', 'owner', 'vehicle']

    def validate(self, data):

        # TODO: Reservation must be a minimum of 1h

        # Check reservation's start date < end date
        if data['start'] > data['end']:
            raise serializers.ValidationError("Reservation's start date must be before of end date")

        reservations = Reservation.objects.filter(vehicle__id=data['vehicle'].id)

        for reservation in reservations:
            if not is_reservation_valid(data, reservation):
                raise serializers.ValidationError("A reservation occurs at the same time.")
        return data


class CreateIncidentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    solved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Incident
        fields = ['id', 'title', 'description', 'owner', 'reservation', 'type', 'solved']


class CreateTicketSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    status = serializers.ChoiceField(choices=TicketStatus.choices, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'date_stored', 'description', 'reservation', 'owner', 'status']


# Include reservations of vehicle. Perfect a single vehicle.
class DetailedVehicleSerializer(serializers.ModelSerializer):
    type = SimpleVehicleTypeSerializer()
    fleet = SimpleFleetSerializer()
    reservations = SimpleReservationSerializer(many=True)

    class Meta:
        model = Vehicle
        fields = ['id', 'name', 'date_stored', 'type', 'fleet', 'reservations']
