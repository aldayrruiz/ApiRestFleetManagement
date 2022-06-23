from django.db import models

from applications.reports.models.abstract_report import AbstractReport
from applications.tenants.models import Tenant


class PunctualityReport(AbstractReport):
    take_out = models.DecimalField()  # Recogido antes de que la reserva haya comenzado (horas).
    take_in = models.DecimalField()  # Recogido después de que la reserva haya comenzado (horas).
    free_in = models.DecimalField()  # Liberado antes de que la reserva haya terminado (horas).
    free_out = models.DecimalField()  # Liberado después de que la reserva haya terminado (horas).
    not_taken = models.DecimalField()  # La reserva no se ha levado acabo (horas).
    tenant = models.ForeignKey(Tenant, related_name='punctuality_reports', on_delete=models.CASCADE)

    class Meta:
        db_table = 'PunctualityReport'
