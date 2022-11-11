from applications.tenants.models import Tenant, TenantBillingMonthlyPdfReport


def get_tenants_queryset():
    return Tenant.objects.all()


def get_billing_reports(user):
    return TenantBillingMonthlyPdfReport.objects.filter(tenant=user.tenant)
