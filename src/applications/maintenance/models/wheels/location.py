from django.db import models
from django.utils.translation import gettext_lazy as _


class WheelsLocation(models.TextChoices):
    # Name = 'Value', _('Label')
    Front = 'Front', _('Front')
    Back = 'Back', _('Back')
    Both = 'Both', _('Both')
