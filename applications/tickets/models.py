import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.reservations.models import Reservation


class TicketStatus(models.TextChoices):
    UNSOLVED = 'UNSOLVED', _('Unsolved')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    DENIED = 'DENIED', _('Denied')


class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=50)
    date_stored = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    reservation = models.ForeignKey(Reservation, related_name='tickets', on_delete=models.CASCADE)
    # Person who request other person to cancel his reservation.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tickets', on_delete=models.CASCADE)

    status = models.CharField(
        max_length=8,
        choices=TicketStatus.choices,
        default=TicketStatus.UNSOLVED
    )

    class Meta:
        db_table = 'Ticket'

    def __str__(self):
        return '{0} - {1}'.format(self.title, self.status)
