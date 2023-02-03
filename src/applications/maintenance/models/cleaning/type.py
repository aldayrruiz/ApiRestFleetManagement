from django.db import models
from django.utils.translation import gettext_lazy as _


class CleaningType(models.TextChoices):
    # Name = 'Value', _('Label')
    Inside = 'Inside', _('Inside')
    Outside = 'Outside', _('Outside')
