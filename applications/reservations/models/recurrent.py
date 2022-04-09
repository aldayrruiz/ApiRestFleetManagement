import uuid

from django.conf import settings
from django.db import models

from applications.tenant.models import Tenant


class Recurrent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    weekdays = models.CharField(max_length=13)  # 0,1,2,3,4,5,6
    since = models.DateTimeField()
    until = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recurrences', on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, related_name='recurrences', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Recurrent'
