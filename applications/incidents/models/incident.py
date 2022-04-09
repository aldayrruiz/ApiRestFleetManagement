import uuid

from django.conf import settings
from django.db import models

from applications.incidents.models import IncidentType
from applications.reservations.models import Reservation
from applications.tenant.models import Tenant


class Incident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date_stored = models.DateTimeField(auto_now_add=True)
    description = models.TextField(default='', blank=True)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='incidents', on_delete=models.CASCADE)
    photo = models.ImageField(default='incidents/none.png', upload_to='incidents')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_incidents',
        null=True,
        on_delete=models.SET_NULL
    )
    solver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='solved_incidents',
        null=True,
        on_delete=models.SET_NULL
    )

    type = models.CharField(
        max_length=14,
        choices=IncidentType.choices,
        default=IncidentType.OTHERS
    )
    solved = models.BooleanField(default=False)

    class Meta:
        db_table = 'Incident'
        ordering = ['-date_stored']

    def __str__(self):
        return self.description
