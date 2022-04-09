import factory

from applications.tenant.tests.factories import TenantFactory
from applications.users.models import User, Role


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker('email')
    tenant = factory.SubFactory(TenantFactory)
    fullname = factory.Faker('name')
    role = Role.USER
