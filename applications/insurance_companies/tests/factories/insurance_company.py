from applications.insurance_companies.models import InsuranceCompany
from applications.tenants.tests.factories import TenantFactory
from shared.test.faker import CustomFactory

factory = CustomFactory().get()


class InsuranceCompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InsuranceCompany

    name = factory.Faker('company')
    phone = factory.Faker('phone_number')
    tenant = factory.SubFactory(TenantFactory)
