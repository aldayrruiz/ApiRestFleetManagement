from django.db import models
from django.utils.translation import gettext_lazy as _


class TicketStatus(models.TextChoices):
    UNSOLVED = 'UNSOLVED', _('Unsolved')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    DENIED = 'DENIED', _('Denied')
