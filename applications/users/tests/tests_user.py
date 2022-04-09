from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.status import *
from rest_framework.test import APITestCase

from shared.test.setup import SetupTest

UserModel = get_user_model()

user_email = 'test.user@test.com'
user_username = 'testUser'
user_password = 't€5t1ngUs€rPa55w0rd'

paths = {
    'users': '/api/users/',
}


class UserTestCase(APITestCase):
    def setUp(self):
        self.client = self.client_class()

        # Create admin & user
        [admin, _] = SetupTest.run()
        self.admin = admin
        self.tenant = admin.tenant

    # Testing LIST

    def test_admin_should_be_able_to_access_users(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-list')
        response = self.client.get(url)
        assert response.status_code == HTTP_200_OK

    def test_user_should_be_able_to_access_users(self):
        user = UserModel.objects.create_user(user_email, user_username, self.tenant.id, user_password)
        self.client.force_authenticate(user=user)
        url = reverse('users-list')
        response = self.client.get(url)
        assert response.status_code == HTTP_200_OK

    # TESTING RETRIEVE

    def test_admin_should_be_able_to_access_user(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('users-detail', args=[str(self.admin.id)])
        response = self.client.get(url)
        assert response.status_code == HTTP_200_OK

    def test_user_should_be_able_to_access_user(self):
        user = UserModel.objects.create_user(user_email, user_username, self.tenant.id, user_password)
        self.client.force_authenticate(user=user)
        path = paths['users'] + str(user.id) + '/'
        response = self.client.get(path)
        assert response.status_code == HTTP_200_OK

    # TESTING DESTROY

    def test_admin_should_not_be_able_to_delete_himself(self):
        self.client.force_authenticate(user=self.admin)
        path = paths['users'] + str(self.admin.id) + '/'
        response = self.client.delete(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_admin_should_be_able_to_delete_users(self):
        self.client.force_authenticate(user=self.admin)
        user = UserModel.objects.create_user(user_email, user_username, self.tenant.id, user_password)
        path = paths['users'] + str(user.id) + '/'
        response = self.client.delete(path)
        assert response.status_code == HTTP_204_NO_CONTENT

    def test_user_should_not_be_able_to_delete_user(self):
        user = UserModel.objects.create_user(user_email, user_username, self.tenant.id, user_password)
        self.client.force_authenticate(user=user)
        path = paths['users'] + str(user.id) + '/'
        response = self.client.delete(path)
        assert response.status_code == HTTP_403_FORBIDDEN
