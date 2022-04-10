from django.db import models
from django.utils.translation import gettext_lazy as _


class Fuel(models.TextChoices):
    DIESEL = 'DIESEL', _('Diesel')
    GASOLINE = 'GASOLINE', _('Gasoline')
    ELECTRIC = 'ELECTRIC', _('Electric')
