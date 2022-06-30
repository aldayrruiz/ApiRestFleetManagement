from rest_framework import serializers

from applications.auth.services.password_changer import PasswordChanger
from applications.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fullname', 'ble_user_id']

    def save(self, tenant):
        user = User(email=self.validated_data['email'],
                    fullname=self.validated_data['fullname'],
                    ble_user_id=self.validated_data['ble_user_id'],
                    tenant=tenant)

        password_changer = PasswordChanger(user)
        password_changer.send_email()
        return user
