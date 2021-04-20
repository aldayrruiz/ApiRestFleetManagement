from django.db import models
from django.utils.translation import gettext_lazy as _


class IncidentType(models.TextChoices):
    # Name = 'Value', _('Label')
    PINCHAZO = 'PI', _('Pinchazo')
    GOLPE = 'GO', _('Golpe')
    PROBLEMAS_DE_USO = 'PU', _('Problemas de uso')
    OTRO = 'OT', _('Otro')


class TicketStatus(models.TextChoices):
    UNSOLVED = 'UNSOLVED', _('Unsolved')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    DENIED = 'DENIED', _('Denied')

