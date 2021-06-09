from django.contrib.auth import get_user_model
from rest_framework import serializers

from applications.vehicles.serializers.simple import SimpleVehicleSerializer


class SingleUserSerializer(serializers.ModelSerializer):
    allowed_vehicles = SimpleVehicleSerializer(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username', 'date_joined', 'allowed_vehicles', 'is_disabled']


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'username', 'password', 'date_joined', 'is_disabled']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', instance.password)
        instance.set_password(password)
        instance.save()
        return instance
