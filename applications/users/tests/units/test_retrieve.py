from django.urls import reverse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.users.tests.factories import UserFactory
from shared.test.setup import SetupTest


class RetrieveUserTestCase(APITestCase):
    def setUp(self):
        # Just for IDE auto-completion
        self.client = self.client_class()

        # Create two tenants and two admins
        [admin, _] = SetupTest.run()
        self.admin_requester = admin
        self.user_requester = UserFactory.create(tenant=admin.tenant)

        self.disabled_user = UserFactory.create(tenant=admin.tenant, is_disabled=True)

    def testAdminShouldGetDisabledUserWhenEvenDisabledQueryIsTrue(self):
        # Given
        self.client.force_authenticate(user=self.admin_requester)
        url = reverse('users-detail', args=[self.disabled_user.id])

        # When
        response = self.client.get(url + '?evenDisabled=True')
        user = response.data

        # Assert
        assert response.status_code == status.HTTP_200_OK, f'User was not found'
        assert str(self.disabled_user.id) == user['id'], f'{user.id} id expected, got {user.id}'

    def testAdminShouldNotGetDisabledUserWhenEvenDisableQueryIsFalse(self):
        # Given
        self.client.force_authenticate(user=self.admin_requester)
        url = reverse('users-detail', args=[self.disabled_user.id])

        # When
        response = self.client.get(url + '?evenDisabled=False')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND, f'Disabled user was found when evenDisabled is False'

    def testUserShouldNotGeDisabledUserWhenEvenDisabledQueryIsTrue(self):
        # Given
        self.client.force_authenticate(user=self.user_requester)
        url = reverse('users-detail', args=[self.disabled_user.id])

        # When
        response = self.client.get(url + '?evenDisabled=True')

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND, 'Disabled user was found when evenDisabled is True'
