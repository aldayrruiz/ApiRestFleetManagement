import uuid

from django.db import models

from applications.tenants.models.tenant import Tenant


class InsuranceCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    tenant = models.ForeignKey(Tenant, related_name='insurance_companies', on_delete=models.CASCADE)

    class Meta:
        db_table = 'Insurance Company'

    def __str__(self):
        return self.name
