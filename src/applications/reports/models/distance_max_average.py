from django.db import models

from applications.reports.models.abstract_report import AbstractReport
from applications.tenants.models import Tenant


class DistanceMaxAverageReport(AbstractReport):
    distance = models.DecimalField()
    max_speed = models.DecimalField()
    average_speed = models.DecimalField()
    tenant = models.ForeignKey(Tenant, related_name='distance_max_average_reports', on_delete=models.CASCADE)

    class Meta:
        db_table = 'DistanceMaxAverageReport'
