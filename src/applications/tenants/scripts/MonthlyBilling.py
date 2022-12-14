import os

from dateutil.relativedelta import relativedelta

from applications.tenants.models import Tenant, TenantBillingMonthlyPdfReport
from applications.tenants.services.email.billing import TenantBillingEmail
from applications.tenants.services.pdf.billing import TenantBillingMonthlyPdfReportGenerator
from applications.tenants.services.pdf.path import TenantBillingMonthlyPdfReportPath
from utils.dates import get_now_utc


# Main
now = get_now_utc()
previous_month = now - relativedelta(months=1)
month = previous_month.month
year = previous_month.year

tenants = Tenant.objects.all()


for tenant in tenants:
    # Generar informe pdf
    pdf = TenantBillingMonthlyPdfReportGenerator(tenant, month, year)
    pdf.generate()

    # If report is already generated delete pdf and update report
    report = TenantBillingMonthlyPdfReport.objects.filter(tenant=tenant, month=month, year=year).first()
    if report:
        report.delete()

    path = TenantBillingMonthlyPdfReportPath.get_pdf(tenant, month, year)
    pdf.output(path)

    # Guardar información sobre el pdf (path, fecha)
    report = TenantBillingMonthlyPdfReport(pdf=path, month=month, year=year, tenant=tenant)
    report.save()
    # Enviar email a los admins
    sender = TenantBillingEmail(tenant, report)
    sender.send()
