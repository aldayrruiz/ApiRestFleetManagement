from django.db import models
from django.utils.translation import gettext_lazy as _


class IncidentType(models.TextChoices):
    # Name = 'Value', _('Label')
    TIRE_PUNCTURE = 'TIRE_PUNCTURE', _('Pinchazo')
    BANG = 'BANG', _('Golpe')
    USAGE_PROBLEMS = 'USAGE_PROBLEMS', _('Problemas de uso')
    LIGHTS = 'LIGHTS', _('Luces')
    OTHERS = 'OTHERS', _('Otros')
