from rest_framework import serializers

from reservations.serializers.simple import SimpleReservationSerializer
from tickets.models import Ticket
from users.serializers.simple import SimpleUserSerializer


class SimpleTicketSerializer(serializers.ModelSerializer):
    reservation = SimpleReservationSerializer()
    owner = SimpleUserSerializer()

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'date_stored', 'description', 'reservation', 'owner', 'status']
