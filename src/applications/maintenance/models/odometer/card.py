import uuid

from django.db import models
from applications.tenants.models import Tenant


class OdometerCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, related_name='odometer_card', on_delete=models.CASCADE)
    km_period = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    date_stored = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'OdometerCard'
