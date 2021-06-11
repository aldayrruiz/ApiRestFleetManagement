from django.contrib.auth import get_user_model
from rest_framework import serializers


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'name', 'surname', 'date_joined', 'is_disabled']
