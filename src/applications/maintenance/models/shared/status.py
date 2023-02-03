from django.db import models
from django.utils.translation import gettext_lazy as _


class MaintenanceStatus(models.TextChoices):
    # Name = 'Value', _('Label')
    NEW = 'NEW', _('NEW')  # When a new itv is created, this is the default status.
    PENDING = 'PENDING', _('PENDING')  # When itv.date + itv_card.date_period has passed
    EXPIRED = 'EXPIRED', _('EXPIRED')  # When the next_revision has already passed
    COMPLETED = 'COMPLETED', _('COMPLETED')  # If a new itv is created, the previous one is completed
