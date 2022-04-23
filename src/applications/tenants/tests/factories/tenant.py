from applications.tenants.models import Tenant
from shared.test.faker import CustomFactory

factory = CustomFactory().get()


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant

    name = factory.Faker('company')
