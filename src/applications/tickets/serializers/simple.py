from rest_framework import serializers

from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.tickets.models import Ticket
from applications.users.serializers.simple import SimpleUserSerializer


class SimpleTicketSerializer(serializers.ModelSerializer):
    reservation = SimpleReservationSerializer()
    owner = SimpleUserSerializer()

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'date_stored', 'description', 'reservation', 'owner', 'status']
