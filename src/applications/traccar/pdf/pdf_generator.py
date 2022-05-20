from applications.tenants.models import Tenant


# Create a pdf for all tenants
class PdfGenerator:
    def __init__(self):
        self.tenants = Tenant.objects.all()


    def generate_pdfs(self):
        for tenant in self.tenants:
            self.generate_pdf(tenant)

    def generate_pdf(self, tenant):
        print()

    def create_graphs(self):
        print()


