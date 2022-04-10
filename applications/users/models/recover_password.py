import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.tenants.models import Tenant

CODE_LENGTH = 6


class RecoverPasswordStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    COMPLETED = 'COMPLETED', _('Completed')


class RecoverPassword(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date_stored = models.DateTimeField(auto_now_add=True)
    code = models.CharField(
        max_length=CODE_LENGTH,
        validators=[MinLengthValidator(CODE_LENGTH)],
        unique=False
    )
    status = models.CharField(
        max_length=9,
        choices=RecoverPasswordStatus.choices,
        default=RecoverPasswordStatus.PENDING
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recover_passwords', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='recover_passwords', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Recover Password'
        ordering = ['-date_stored']

    def __str__(self):
        return '{} - {}'.format(self.code, self.status)
