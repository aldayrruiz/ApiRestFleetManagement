from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from applications.insurance_companies.models import InsuranceCompany
from applications.vehicles.models import Vehicle, Fuel, VehicleType


class CreateOrUpdateVehicleSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, validators=[UniqueValidator(queryset=Vehicle.objects.all())])
    model = serializers.CharField(max_length=50)
    brand = serializers.CharField(max_length=20)
    number_plate = serializers.CharField(max_length=8,
                                         min_length=7)
    is_disabled = serializers.BooleanField(required=False)
    fuel = serializers.ChoiceField(choices=Fuel.choices, required=False)
    type = serializers.ChoiceField(choices=VehicleType.choices, required=False)
    gps_device = serializers.CharField(max_length=20)
    insurance_company = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=InsuranceCompany.objects.all(),
                                                           required=False)
    policy_number = serializers.CharField(allow_blank=True, max_length=20, required=False)
    icon = serializers.IntegerField(required=False)

    def create(self, validated_data):
        return Vehicle.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.model = validated_data.get('model', instance.model)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.number_plate = validated_data.get('number_plate', instance.number_plate)
        instance.is_disabled = validated_data.get('is_disabled', instance.is_disabled)
        instance.fuel = validated_data.get('fuel', instance.fuel)
        instance.type = validated_data.get('type', instance.type)
        instance.gps_device = validated_data.get('gps_device', instance.gps_device)
        instance.insurance_company = validated_data.get('insurance_company', instance.insurance_company)
        instance.policy_number = validated_data.get('policy_number', instance.policy_number)
        instance.icon = validated_data.get('icon', instance.icon)
        instance.save()
        return instance
