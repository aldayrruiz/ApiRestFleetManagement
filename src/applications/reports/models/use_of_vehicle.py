from django.db import models
from applications.reports.models.abstract_report import AbstractReport
from applications.tenants.models import Tenant


class AbstractUseOfVehicleReport(AbstractReport):
    hours = models.DecimalField(max_digits=10, decimal_places=5)

    class Meta:
        abstract = True


class TheoreticalUseOfVehicleReport(AbstractUseOfVehicleReport):
    tenant = models.ForeignKey(Tenant, related_name='theoretical_use_of_vehicle_reports', on_delete=models.CASCADE)

    class Meta:
        db_table = 'TheoreticalUseOfVehicleReport'


class RealUseOfVehicleReport(AbstractUseOfVehicleReport):
    tenant = models.ForeignKey(Tenant, related_name='real_use_of_vehicle_reports', on_delete=models.CASCADE)

    class Meta:
        db_table = 'RealUseOfVehicleReport'
