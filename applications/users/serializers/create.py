from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.users.models import Role, User


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    role = serializers.ChoiceField(choices=Role.choices)

    class Meta:
        model = get_user_model()
        fields = ['email', 'fullname', 'role', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(email=self.validated_data['email'],
                    fullname=self.validated_data['fullname'],
                    role=self.validated_data['role'])

        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})

        user.set_password(password)
        user.save()
        return user
