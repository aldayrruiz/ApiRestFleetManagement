from rest_framework import serializers

from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.tickets.models import Ticket
from applications.users.serializers.simple import SimpleUserSerializer
from applications.vehicles.serializers.simple import SimpleVehicleSerializer


class SimpleTicketSerializer(serializers.ModelSerializer):
    reservation = SimpleReservationSerializer()
    owner = SimpleUserSerializer()
    reservation_owner = SimpleUserSerializer()
    reservation_vehicle = SimpleVehicleSerializer()

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'date_stored', 'description', 'reservation', 'owner', 'status',
                  'reservation_owner', 'reservation_vehicle', 'reservation_start', 'reservation_end',
                  'reservation_title', 'reservation_description']
