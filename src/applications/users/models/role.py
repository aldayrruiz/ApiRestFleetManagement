from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    """
    Super admin access to mobile app and admin website. But he can change his tenant when login.
    Admin has access to mobile app and admin website.
    User has access only to mobile app.

    """
    SUPER_ADMIN = 'SUPER_ADMIN', _('SuperAdmin')
    ADMIN = 'ADMIN', _('Admin')
    USER = 'USER', _('User')
