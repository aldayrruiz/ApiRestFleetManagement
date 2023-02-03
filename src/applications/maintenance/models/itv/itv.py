import uuid

from django.conf import settings
from django.db import models

from applications.maintenance.models.shared.status import MaintenanceStatus
from applications.tenants.models import Tenant
from applications.vehicles.models import Vehicle


class Itv(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='itvs', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='itvs')
    date = models.DateTimeField()
    place = models.TextField()
    passed = models.BooleanField()
    next_revision = models.DateTimeField()
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=14, choices=MaintenanceStatus.choices, default=MaintenanceStatus.NEW)
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='itvs', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Itv'
