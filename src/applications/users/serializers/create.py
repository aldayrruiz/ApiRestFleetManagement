from rest_framework import serializers
from rest_framework.fields import ChoiceField

from applications.auth.services.password_changer import PasswordChanger
from applications.users.models import User, Role


class RegistrationSerializer(serializers.ModelSerializer):
    role = ChoiceField(choices=[Role.USER, Role.ADMIN], required=True)

    class Meta:
        model = User
        fields = ['email', 'fullname', 'role', 'ble_user_id', 'tenant']

    def save(self):
        user = User(email=self.validated_data['email'],
                    fullname=self.validated_data['fullname'],
                    role=self.validated_data['role'],
                    ble_user_id=self.validated_data['ble_user_id'],
                    tenant=self.validated_data['tenant'])
        password_changer = PasswordChanger(user)
        password_changer.send_email()
        return user
