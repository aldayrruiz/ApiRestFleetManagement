import uuid

from django.conf import settings
from django.db import models

from applications.reservations.models.reservation import Reservation
from applications.tenants.models.tenant import Tenant
from applications.tickets.models.status import TicketStatus
from applications.vehicles.models import Vehicle


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    date_stored = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    reservation = models.ForeignKey(Reservation, null=True, related_name='tickets', on_delete=models.SET_NULL)
    # Person who request other person to cancel his reservation.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='tickets', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=8,
        choices=TicketStatus.choices,
        default=TicketStatus.UNSOLVED
    )

    # Reservation data (if reservation is deleted, ticket is still available)
    reservation_title = models.CharField(default='', max_length=50)
    reservation_description = models.TextField(default='', blank=True)
    reservation_owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    reservation_vehicle = models.ForeignKey(Vehicle, null=True, on_delete=models.CASCADE)
    reservation_start = models.DateTimeField(default=None, null=True)
    reservation_end = models.DateTimeField(default=None, null=True)

    class Meta:
        db_table = 'Ticket'
        ordering = ['-date_stored']

    def __str__(self):
        return '{0} - {1}'.format(self.title, self.status)
