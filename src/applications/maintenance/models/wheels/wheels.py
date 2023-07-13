import uuid

from django.conf import settings
from django.db import models

from applications.maintenance.models.shared.cause_status import CauseStatus
from applications.maintenance.models.shared.status import MaintenanceStatus
from applications.maintenance.models.wheels.location import WheelsLocation
from applications.maintenance.models.wheels.operation import WheelsOperation
from applications.tenants.models import Tenant
from applications.vehicles.models import Vehicle


class Wheels(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='wheels', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='wheels')
    date = models.DateTimeField()
    location = models.CharField(max_length=10, choices=WheelsLocation.choices, default=WheelsLocation.Front)
    kilometers = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    operation = models.CharField(max_length=12, choices=WheelsOperation.choices, default=WheelsOperation.Inspection)
    passed = models.BooleanField(default=False)
    next_revision = models.DateTimeField(null=True, blank=True)
    next_kilometers = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    completed = models.BooleanField(default=False)
    cause_status = models.CharField(max_length=14, choices=CauseStatus.choices, default=CauseStatus.KILOMETERS)
    status = models.CharField(max_length=14, choices=MaintenanceStatus.choices, default=MaintenanceStatus.NEW)
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='wheels', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Wheels'
