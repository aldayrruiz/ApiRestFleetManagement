from rest_framework import serializers

from applications.users.models import User
from utils.email.users import send_created_user_email
from utils.password.generator import generate_password


class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'fullname']

    def save(self, tenant):
        user = User(email=self.validated_data['email'],
                    fullname=self.validated_data['fullname'],
                    tenant=tenant)

        password = generate_password()

        user.set_password(password)
        user.save()
        send_created_user_email(user, password)
        return user

