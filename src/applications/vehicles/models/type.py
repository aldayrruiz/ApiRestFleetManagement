from django.db import models
from django.utils.translation import gettext_lazy as _


class VehicleType(models.TextChoices):
    TOURISM = 'TOURISM', _('Turismo')
    ALL_TERRAIN = 'ALL_TERRAIN', _('Todo terreno')
    MOTORCYCLE = 'MOTORCYCLE', _('Motocicleta')
    VAN = 'VAN', _('Furgoneta')
    TRUCK = 'TRUCK', _('Camión')
