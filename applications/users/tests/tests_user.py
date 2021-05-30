from django.contrib.auth import get_user_model
from rest_framework.status import *
from rest_framework.test import APITestCase

UserModel = get_user_model()

admin_email = 'test.admin@test.com'
admin_username = 'testAdmin'
admin_password = 't€5t1ngAdm1nPa55w0rd'

user_email = 'test.user@test.com'
user_username = 'testUser'
user_password = 't€5t1ngUs€rPa55w0rd'

paths = {
    'users': '/api/users/',
}


class UserTestCase(APITestCase):

    client = None
    admin = None
    user = None

    def setUp(self):
        self.client = self.client_class()

        # Create admin & user
        self.admin = UserModel.objects.create_superuser(admin_email, admin_username, admin_password)
        self.user = UserModel.objects.create_user(user_email, user_username, user_password)

    # TESTING LIST

    def test_admin_should_be_able_to_access_users(self):
        # Authenticate as admin for next requests
        self.client.force_authenticate(user=self.admin)
        # Test list endpoint: /api/users/
        response = self.client.get(paths['users'])
        assert response.status_code == HTTP_200_OK

    def test_user_should_not_be_able_to_access_users(self):
        # Authenticate as user for next requests
        self.client.force_authenticate(user=self.user)
        # test destroy endpoint: /api/users/uuid/
        path = paths['users'] + str(self.admin.id) + '/'
        response = self.client.get(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    # TESTING RETRIEVE

    def test_admin_should_be_able_to_access_user(self):
        # Authenticate as admin for next requests
        self.client.force_authenticate(user=self.admin)
        # Test retrieve endpoint: /api/users/uuid/
        path = paths['users'] + str(self.admin.id) + '/'
        response = self.client.get(path)
        assert response.status_code == HTTP_200_OK

    def test_user_should_not_be_able_to_access_user(self):
        # Authenticate as admin for next requests
        self.client.force_authenticate(user=self.user)
        # Test retrieve endpoint: /api/users/uuid/
        path = paths['users'] + str(self.admin.id) + '/'
        response = self.client.get(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    # TESTING DESTROY

    def test_admin_should_not_be_able_to_delete_himself(self):
        # Authenticate as admin for next requests
        self.client.force_authenticate(user=self.admin)
        # test destroy endpoint: /api/users/uuid/
        path = paths['users'] + str(self.admin.id) + '/'
        response = self.client.delete(path)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_admin_should_be_able_to_delete_users(self):
        # Authenticate as admin for next requests
        self.client.force_authenticate(user=self.admin)
        # test destroy endpoint: /api/users/uuid/
        path = paths['users'] + str(self.user.id) + '/'
        response = self.client.delete(path)
        assert response.status_code == HTTP_204_NO_CONTENT

    def test_user_should_not_be_able_to_delete_user(self):
        # Authenticate as admin for next requests
        self.client.force_authenticate(user=self.user)
        # test destroy endpoint: /api/users/uuid/
        path = paths['users'] + str(self.user.id) + '/'
        response = self.client.delete(path)
        assert response.status_code == HTTP_403_FORBIDDEN
