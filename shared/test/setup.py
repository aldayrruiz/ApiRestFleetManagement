from django.contrib.auth import get_user_model

from applications.tenants.tests.factories import TenantFactory
from applications.users.tests.factories import AdminFactory


UserModel = get_user_model()


class SetupTest:

    @staticmethod
    def run():
        """
        Create two tenants and two admins.
        :return: Two admins that belong to two different tenants
        """
        tenant1 = TenantFactory.create()
        tenant2 = TenantFactory.create()
        admin1 = AdminFactory.create(tenant=tenant1)
        admin2 = AdminFactory.create(tenant=tenant2)
        return [admin1, admin2]
