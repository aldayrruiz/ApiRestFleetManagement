from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from applications.users.models import User, RecoverPassword
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from utils.codegen import generate_recover_password_code


class SingleUserSerializer(serializers.ModelSerializer):
    allowed_vehicles = SimpleVehicleSerializer(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'fullname', 'date_joined', 'allowed_vehicles', 'is_disabled']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'fullname', 'password', 'date_joined', 'is_disabled']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        password = validated_data.get('password', instance.password)
        instance.set_password(password)
        instance.save()
        return instance


class PartialUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['is_disabled']


class CreateRecoverPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = RecoverPassword
        fields = ['email']

    def save(self):
        queryset = User.objects.all()
        code = generate_recover_password_code()
        owner = get_object_or_404(queryset, email=self.validated_data['email'])
        recover_password = RecoverPassword(owner=owner, code=code, tenant=owner.tenant)
        recover_password.save()
        return recover_password


class RecoverPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecoverPassword
        fields = ['id', 'status']


class ConfirmRecoverPasswordSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
