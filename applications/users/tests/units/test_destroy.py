from django.urls import reverse
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from applications.users.tests.factories import UserFactory
from shared.test.setup import SetupTest


class DestroyUserTestCase(APITestCase):
    def setUp(self):
        # Just for IDE auto-completion
        self.client = self.client_class()

        # Create two tenants and two admins
        [admin, _] = SetupTest.run()
        self.admin_requester = admin
        self.user_requester = UserFactory.create(tenant=admin.tenant)

        self.user_to_destroy = UserFactory.create(tenant=admin.tenant)

    def testAdminShouldBeAbleToDeleteAUser(self):
        # Given
        self.client.force_authenticate(user=self.admin_requester)
        url = reverse('users-detail', args=[self.user_to_destroy.id])

        # When
        response = self.client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT, f'User was not found'

    def testAdminShouldNotBeAbleToDeleteHimself(self):
        # Given
        self.client.force_authenticate(user=self.admin_requester)
        url = reverse('users-detail', args=[self.admin_requester.id])

        # When
        response = self.client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Admin was able to delete himself'

    def testUserShouldNotBeAbleToDeleteAUser(self):
        # Given
        self.client.force_authenticate(user=self.user_requester)
        url = reverse('users-detail', args=[self.user_to_destroy.id])

        # When
        response = self.client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN, f'Regular user delete other user (Only admins)'
