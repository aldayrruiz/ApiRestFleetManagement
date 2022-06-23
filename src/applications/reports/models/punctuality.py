from django.db import models

from applications.reports.models.abstract_report import AbstractReport
from applications.tenants.models import Tenant


class PunctualityReport(AbstractReport):
    take_out = models.DecimalField(max_digits=10, decimal_places=5)  # Recogido antes de que la reserva haya comenzado (horas).
    take_in = models.DecimalField(max_digits=10, decimal_places=5)  # Recogido después de que la reserva haya comenzado (horas).
    free_in = models.DecimalField(max_digits=10, decimal_places=5)  # Liberado antes de que la reserva haya terminado (horas).
    free_out = models.DecimalField(max_digits=10, decimal_places=5)  # Liberado después de que la reserva haya terminado (horas).
    not_taken = models.DecimalField(max_digits=10, decimal_places=5)  # La reserva no se ha levado acabo (horas).
    tenant = models.ForeignKey(Tenant, related_name='punctuality_reports', on_delete=models.CASCADE)

    class Meta:
        db_table = 'PunctualityReport'
