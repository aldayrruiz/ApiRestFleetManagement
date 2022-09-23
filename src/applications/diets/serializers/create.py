from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from applications.diets.models import DietPayment, DietPhoto, Diet
from applications.diets.serializers.simple import DietPaymentSerializer


class CreateDietSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    completed = serializers.ReadOnlyField(default=False)
    payments = DietPaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Diet
        fields = ['id', 'reservation', 'start', 'end', 'owner', 'payments', 'completed']


class CreateDietPaymentSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DietPayment
        fields = ['id', 'owner', 'diet', 'type', 'liters', 'amount', 'description']


class CreateDietPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = DietPhoto
        fields = ['id', 'owner', 'payment', 'photo']
