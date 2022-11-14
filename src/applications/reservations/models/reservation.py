import uuid

from django.conf import settings
from django.db import models

from applications.reservations.models.recurrent import Recurrent
from applications.tenants.models.tenant import Tenant
from applications.vehicles.models.vehicle import Vehicle


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    date_stored = models.DateTimeField(auto_now_add=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(default='', blank=True)
    is_cancelled = models.BooleanField(default=False)
    is_recurrent = models.BooleanField(default=False)
    is_driver_needed = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reservations', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, related_name='reservations', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='reservations', on_delete=models.CASCADE)

    recurrent = models.ForeignKey(Recurrent,
                                  blank=True,
                                  null=True,
                                  default=None,
                                  related_name='reservations',
                                  on_delete=models.CASCADE)

    incidents = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='incidents.Incident',
        through_fields=('reservation', 'owner'),
        related_name='incidents'
    )

    class Meta:
        db_table = 'Reservation'
        ordering = ['-start']

    def __str__(self):
        return '{0} - {1}'.format(self.owner, self.title)
