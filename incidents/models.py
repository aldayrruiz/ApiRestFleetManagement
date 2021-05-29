import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from reservations.models import Reservation


class IncidentType(models.TextChoices):
    # Name = 'Value', _('Label')
    TIRE_PUNCTURE = 'TIRE_PUNCTURE', _('Tire puncture')
    BANG = 'BANG', _('Bang')
    USAGE_PROBLEMS = 'USAGE_PROBLEMS', _('Usage problems')
    OTHERS = 'OTHERS', _('Others')


class Incident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    date_stored = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    # This position will be the last position of the vehicle when an incident is reported.
    # position = models.OneToOneField(Track, null=True, on_delete=models.SET_NULL)

    type = models.CharField(
        max_length=14,
        choices=IncidentType.choices,
        default=IncidentType.OTHERS
    )

    solved = models.BooleanField(default=False)

    class Meta:
        db_table = 'Incident'

    def __str__(self):
        return self.title
