from pathlib import Path

from decouple import config

from applications.tenants.models import Tenant
from shared.pdf.path.logo import LogoPdfPath


BASE_DIR = Path(config('PDF_PATH'))
DIETS_DIR = BASE_DIR / 'diets'
ASSETS = BASE_DIR / 'assets'


class DietsPdfPath(LogoPdfPath):

    @staticmethod
    def get_tenant(tenant: Tenant):
        return str(DIETS_DIR / tenant.short_name)

    @staticmethod
    def get_pdf(tenant: Tenant, month: int, year: int):
        return str(DIETS_DIR / f'{str(tenant.short_name)}_{month}_{year}.pdf')
