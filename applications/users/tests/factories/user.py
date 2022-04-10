from applications.tenants.tests.factories import TenantFactory
from applications.users.models import User, Role
from shared.test.faker import CustomFactory

factory = CustomFactory().get()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    tenant = factory.SubFactory(TenantFactory)
    fullname = factory.Faker('name')
    role = Role.USER


class AdminFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    tenant = factory.SubFactory(TenantFactory)
    fullname = factory.Faker('name')
    role = Role.ADMIN
