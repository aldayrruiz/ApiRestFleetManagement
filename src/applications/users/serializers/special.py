from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from applications.users.models import User, RecoverPassword
from applications.vehicles.serializers.simple import SimpleVehicleSerializer
from utils.password.generator import generate_recover_password_code


class SingleUserSerializer(serializers.ModelSerializer):
    allowed_vehicles = SimpleVehicleSerializer(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'fullname', 'date_joined', 'is_disabled', 'role', 'allowed_vehicles', 'ble_user_id',
                  'is_supervisor', 'is_interventor']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'fullname', 'password', 'date_joined', 'is_disabled', 'is_supervisor', 'is_interventor']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.is_supervisor = validated_data.get('is_supervisor', instance.is_supervisor)
        instance.is_interventor = validated_data.get('is_interventor', instance.is_interventor)
        password = validated_data.get('password', instance.password)
        instance.set_password(password)
        instance.save()
        return instance


class PartialUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['ble_user_id', 'is_disabled', 'is_supervisor', 'is_interventor']


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
