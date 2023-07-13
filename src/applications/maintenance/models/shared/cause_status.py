from django.db import models
from django.utils.translation import gettext_lazy as _


class CauseStatus(models.TextChoices):
    # Name = 'Value', _('Label')
    KILOMETERS = 'KILOMETERS', _('KILOMETERS')  # When a revision is changed status by kilometers.
    DATE = 'DATE', _('DATE')  # When revision is changed status by date.
