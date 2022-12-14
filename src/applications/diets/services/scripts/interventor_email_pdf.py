import os

from dateutil.relativedelta import relativedelta

from applications.diets.models import DietMonthlyPdfReport
from applications.diets.services.emails.interventor import DietCompletedInterventorEmail
from applications.diets.services.pdf.monthly import DietMonthlyPdfReportGenerator
from applications.diets.services.pdf.path import DietsPdfPath
from applications.tenants.models import Tenant
from utils.dates import get_now_utc


# Main
now = get_now_utc()
previous_month = now - relativedelta(months=1)
month = previous_month.month
year = previous_month.year

tenants = Tenant.objects.filter(diet=True)

for tenant in tenants:
    # Generar informe pdf
    pdf = DietMonthlyPdfReportGenerator(tenant, month, year)
    pdf.generate()
    path = DietsPdfPath.get_pdf(tenant, month, year)
    pdf.output(path)

    # If report is already generated delete pdf and update report
    report = DietMonthlyPdfReport.objects.filter(tenant=tenant, month=month, year=year).first()
    if report:
        os.remove(report.pdf)
        report.delete()

    # Guardar información sobre el pdf (path, fecha)
    report = DietMonthlyPdfReport(pdf=path, month=month, year=year, tenant=tenant)
    report.save()
    # Enviar email a los interventores
    sender = DietCompletedInterventorEmail(tenant, report)
    sender.send()
