import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.reservations.models import Reservation


class IncidentType(models.TextChoices):
    # Name = 'Value', _('Label')
    TIRE_PUNCTURE = 'TIRE_PUNCTURE', _('Pinchazo')
    BANG = 'BANG', _('Golpe')
    USAGE_PROBLEMS = 'USAGE_PROBLEMS', _('Problemas de uso')
    OTHERS = 'OTHERS', _('Otros')


class Incident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    date_stored = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    photo = models.ImageField(default='incidents/none.png', upload_to='incidents')

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
        return self.title
