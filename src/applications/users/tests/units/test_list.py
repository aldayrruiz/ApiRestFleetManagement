from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from applications.users.tests.factories import UserFactory
from shared.test.setup import SetupTest


class ListUserTestCase(APITestCase):
    def setUp(self):
        # Just for IDE auto-completion
        self.client = self.client_class()

        # endpoint to test
        self.url = reverse('users-list')

        # Create two tenants and two admins
        [admin1, admin2] = SetupTest.run()
        self.admin1 = admin1
        self.admin2 = admin2
        self.tenant1 = admin1.tenant
        self.tenant2 = admin2.tenant

        UserFactory.create_batch(size=3, tenant=self.tenant1, is_disabled=False)
        UserFactory.create_batch(size=1, tenant=self.tenant1, is_disabled=True)

        UserFactory.create_batch(size=2, tenant=self.tenant2)

    def testAdminShouldGetAllUsersWhenEvenDisabledQueryIsTrue(self):
        # Given
        self.client.force_authenticate(user=self.admin1)

        # When
        response = self.client.get(self.url + '?evenDisabled=True')
        users = response.data

        # Assert
        assert len(users) == 5, f'5 users expected, got: {len(users)}'
        assert response.status_code == status.HTTP_200_OK

    def testAdminShouldOnlyGetUsersEnabledWhenEvenDisabledQueryIsFalse(self):
        # Given
        self.client.force_authenticate(user=self.admin1)

        # When
        response = self.client.get(self.url + '?evenDisabled=False')
        users = response.data

        # Assert
        assert len(users) == 4, f'4 users expected, got: {len(users)}'
        assert response.status_code == status.HTTP_200_OK

    def testUserShouldOnlyGetEnabledUsers(self):
        # Given
        requester = UserFactory.create(tenant=self.tenant1)
        self.client.force_authenticate(user=requester)

        # When
        response = self.client.get(self.url + '?evenDisabled=True')
        users = response.data

        # Assert
        assert len(users) == 5, f'5 users expected, got: {len(users)}'
        assert response.status_code == status.HTTP_200_OK
