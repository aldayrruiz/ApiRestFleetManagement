import uuid

from django.conf import settings
from django.db import models

from applications.reservations.models import Reservation
from applications.tenants.models import Tenant
from applications.tickets.models import TicketStatus


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    date_stored = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    reservation = models.ForeignKey(Reservation, related_name='tickets', on_delete=models.CASCADE)
    # Person who request other person to cancel his reservation.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='tickets', on_delete=models.CASCADE)

    status = models.CharField(
        max_length=8,
        choices=TicketStatus.choices,
        default=TicketStatus.UNSOLVED
    )

    class Meta:
        db_table = 'Ticket'
        ordering = ['-date_stored']

    def __str__(self):
        return '{0} - {1}'.format(self.title, self.status)
