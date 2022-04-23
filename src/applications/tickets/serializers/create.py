from rest_framework import serializers

from applications.tickets.models import TicketStatus, Ticket


class CreateTicketSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    status = serializers.ChoiceField(choices=TicketStatus.choices, read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'title', 'date_stored', 'description', 'reservation', 'owner', 'status']
