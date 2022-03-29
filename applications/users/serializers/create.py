from rest_framework import serializers

from applications.auth.services.password_changer import PasswordChanger
from applications.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'fullname']

    def save(self, tenant):
        user = User(email=self.validated_data['email'],
                    fullname=self.validated_data['fullname'],
                    tenant=tenant)

        password_changer = PasswordChanger(user)
        password_changer.send_email()
