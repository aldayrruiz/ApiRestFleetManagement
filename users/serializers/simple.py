from django.contrib.auth import get_user_model
from rest_framework import serializers


class SimpleUserSerializer(serializers.ModelSerializer):
    # allowed_types = SimpleVehicleTypeSerializer(read_only=True, many=True)

    class Meta:
        model = get_user_model()
        # fields = ['id', 'email', 'username', 'date_joined', 'allowed_types']
        fields = ['id', 'email', 'username', 'date_joined']
