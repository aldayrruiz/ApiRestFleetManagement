import uuid

from django.conf import settings
from django.db import models

from applications.tenants.models import Tenant
from applications.vehicles.models import Vehicle


class Repairment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repairments', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='repairments')
    date = models.DateTimeField()
    kilometers = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    location = models.CharField(default='', max_length=50)
    description = models.CharField(default='', max_length=100)
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='repairments', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Repairment'
