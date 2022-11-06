from pathlib import Path

from decouple import config

from applications.tenants.models import Tenant
from shared.pdf.path.logo import LogoPdfPath


BASE_DIR = Path(config('PDF_PATH'))
BILLINGS_DIR = BASE_DIR / 'billings'


class TenantBillingMonthlyPdfReportPath(LogoPdfPath):

    @staticmethod
    def get_tenant(tenant: Tenant):
        return str(BILLINGS_DIR / tenant.short_name)

    @staticmethod
    def get_pdf(tenant: Tenant, month: int, year: int):
        return str(BILLINGS_DIR / f'{str(tenant.short_name)}_{month}_{year}.pdf')
