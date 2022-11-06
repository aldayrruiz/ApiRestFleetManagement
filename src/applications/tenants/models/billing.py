import uuid


from django.db import models
from applications.tenants.models import Tenant


class TenantBillingMonthlyPdfReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    pdf = models.FilePathField()
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    tenant = models.ForeignKey(Tenant, related_name='billings', on_delete=models.CASCADE)

    class Meta:
        db_table = 'TenantBillingMonthlyPdfReport'
