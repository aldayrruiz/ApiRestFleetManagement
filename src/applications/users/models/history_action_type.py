from django.db import models
from django.utils.translation import gettext_lazy as _


class ActionType(models.TextChoices):
    CREATED = 'CREATED', _('Created')
    DELETED = 'DELETED', _('Deleted')