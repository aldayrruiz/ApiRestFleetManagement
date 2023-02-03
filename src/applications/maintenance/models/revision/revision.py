import uuid

from django.conf import settings
from django.db import models

from applications.maintenance.models.shared.status import MaintenanceStatus
from applications.tenants.models import Tenant
from applications.vehicles.models import Vehicle


class Revision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='revisions', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='revisions')
    date = models.DateTimeField()
    kilometers = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    motive = models.TextField()
    garage = models.TextField()
    next_revision = models.DateTimeField()
    next_kilometers = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=14, choices=MaintenanceStatus.choices, default=MaintenanceStatus.NEW)
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='revisions', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Revision'
