from django.db import models
from django.utils.translation import gettext_lazy as _


class WheelsOperation(models.TextChoices):
    # Name = 'Value', _('Label')
    Inspection = 'Inspection', _('Inspection')
    Substitution = 'Substitution', _('Substitution')
