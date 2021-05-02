from django.db import models
from django.utils.translation import gettext_lazy as _


class IncidentType(models.TextChoices):
    # Name = 'Value', _('Label')
    TIRE_PUNCTURE = 'TIRE_PUNCTURE', _('Tire puncture')
    BANG = 'BANG', _('Bang')
    USAGE_PROBLEMS = 'USAGE_PROBLEMS', _('Usage problems')
    OTHERS = 'OTHERS', _('Others')


class TicketStatus(models.TextChoices):
    UNSOLVED = 'UNSOLVED', _('Unsolved')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    DENIED = 'DENIED', _('Denied')


class Role(models.TextChoices):
    """
    Super admin: Create fleet, visualize all fleets, remove and give privileges
    Fleet admin: Just know about his fleet and have create/update/delete privileges
    to create vehicles, create users but cannot crete new fleets.
    User: Just know about his fleet, it has not access to web admin site.
    """
    SUPER_ADMIN = 'SUPER_ADMIN', _('Super admin'),
    FLEET_ADMIN = 'FLEET_ADMIN', _('Fleet admin'),
    USER = 'USER', _('User')

