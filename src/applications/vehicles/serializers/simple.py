from rest_framework import serializers

from applications.insurance_companies.serializers.create import InsuranceCompanySerializer
from applications.traccar.serializers.simple import SimpleDeviceSerializer
from applications.vehicles.models import Vehicle


class SimpleVehicleSerializer(serializers.ModelSerializer):
    gps_device = SimpleDeviceSerializer()
    insurance_company = InsuranceCompanySerializer()

    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'gps_device', 'date_stored', 'is_disabled', 'fuel', 'insurance_company', 'policy_number', 'icon']
