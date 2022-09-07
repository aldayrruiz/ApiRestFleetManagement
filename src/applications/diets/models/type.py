from django.db import models
from django.utils.translation import gettext_lazy as _


class DietType(models.TextChoices):
    # Name = 'Value', _('Label')
    Gasolina = 'Gasolina', _('Gasolina')
    Parking = 'Parking', _('Parking')
    Peaje = 'Peaje', _('Peaje')
    Alojamiento = 'Alojamiento', _('Alojamiento')
    Otros = 'Otros', _('Otros')
