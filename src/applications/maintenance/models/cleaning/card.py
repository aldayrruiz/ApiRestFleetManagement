import uuid

from django.db import models
from applications.tenants.models import Tenant
from applications.vehicles.models import Vehicle


class CleaningCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.OneToOneField(Vehicle, related_name='cleaning_card', on_delete=models.CASCADE)
    date_period = models.CharField(max_length=20, default='', blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        db_table = 'CleaningCard'
