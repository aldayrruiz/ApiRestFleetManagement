from rest_framework import serializers

from applications.incidents.models import Incident
from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.users.serializers.simple import SimpleUserSerializer


class SimpleIncidentSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer()
    reservation = SimpleReservationSerializer()

    class Meta:
        model = Incident
        fields = ['id', 'date_stored', 'description', 'owner', 'reservation', 'type', 'photo', 'solved',
                  'self_responsible', 'solver_message']
