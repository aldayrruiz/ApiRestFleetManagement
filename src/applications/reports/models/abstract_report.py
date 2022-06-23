import uuid


from django.db import models

from applications.reports.models.monthly import MonthlyReport
from applications.vehicles.models import Vehicle


class AbstractReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    monthly_report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE)

    class Meta:
        abstract = True
