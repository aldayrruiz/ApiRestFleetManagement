from applications.insurance_companies.models import InsuranceCompany


def get_insurance_companies_queryset(user):
    return InsuranceCompany.objects.filter(tenant=user.tenant)
