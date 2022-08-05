from django.contrib.auth import get_user_model
from rest_framework import serializers


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id',
                  'email',
                  'fullname',
                  'date_joined',
                  'is_disabled',
                  'role',
                  'allowed_vehicles',
                  'ble_user_id',
                  'is_supervisor',
                  'is_interventor'
                  ]
