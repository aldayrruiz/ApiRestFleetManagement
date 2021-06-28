from rest_framework import serializers

from applications.traccar.models import Device


class SimpleDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = ['id', 'name', 'imei']
