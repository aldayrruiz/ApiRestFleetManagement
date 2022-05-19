from rest_framework import serializers

from applications.insurance_companies.serializers.create import InsuranceCompanySerializer
from applications.reservations.serializers.simple import SimpleReservationSerializer
from applications.traccar.serializers.simple import SimpleDeviceSerializer
from applications.vehicles.models import Vehicle


class DetailedVehicleSerializer(serializers.ModelSerializer):
    gps_device = SimpleDeviceSerializer()
    reservations = SimpleReservationSerializer(many=True)
    insurance_company = InsuranceCompanySerializer()

    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'gps_device', 'date_stored', 'reservations', 'is_disabled',
                  'fuel', 'insurance_company', 'policy_number', 'icon']


class SimpleVehicleSerializer(serializers.ModelSerializer):
    gps_device = SimpleDeviceSerializer()
    insurance_company = InsuranceCompanySerializer()

    class Meta:
        model = Vehicle
        fields = ['id', 'model', 'brand', 'number_plate', 'gps_device', 'date_stored', 'is_disabled', 'fuel',
                  'insurance_company', 'policy_number', 'icon']


class DisableVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['is_disabled']