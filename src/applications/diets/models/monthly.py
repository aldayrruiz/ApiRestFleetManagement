import uuid


from django.db import models
from applications.tenants.models import Tenant


class DietMonthlyPdfReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    pdf = models.FilePathField()
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    date_stored = models.DateTimeField(auto_now_add=True)
    tenant = models.ForeignKey(Tenant, related_name='diet_reports', on_delete=models.CASCADE)

    class Meta:
        db_table = 'DietMonthlyPdfReport'
