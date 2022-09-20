from django.db import models
from django.utils.translation import gettext_lazy as _


class VehicleType(models.TextChoices):
    TOURISM = 'TOURISM', _('TOURISM')
    ALL_TERRAIN = 'ALL_TERRAIN', _('ALL_TERRAIN')
    MOTORCYCLE = 'MOTORCYCLE', _('MOTORCYCLE')
    VAN = 'VAN', _('VAN')
    TRUCK = 'TRUCK', _('TRUCK')
