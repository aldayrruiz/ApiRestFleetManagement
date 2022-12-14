from pathlib import Path

from decouple import config

from applications.tenants.models import Tenant
from shared.pdf.path.logo import LogoPdfPath

BASE_DIR = Path(config('PDF_PATH'))
REPORTS_DIR = BASE_DIR / 'reports'


class ReportsPdfPath(LogoPdfPath):

    @staticmethod
    def get_tenant(tenant: Tenant):
        return str(REPORTS_DIR / tenant.short_name)

    @staticmethod
    def get_graphs(tenant: Tenant):
        return str(REPORTS_DIR / tenant.short_name / 'images')

    @staticmethod
    def get_graph(tenant: Tenant, filename: str):
        return str(REPORTS_DIR / tenant.short_name / 'images' / filename)

    @staticmethod
    def get_pdf(tenant: Tenant, month: int, year: int):
        return str(REPORTS_DIR / f'{str(tenant.short_name)}_{month}_{year}.pdf')
