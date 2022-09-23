from rest_framework import serializers

from applications.diets.models import DietPayment, DietPhoto, Diet
from applications.users.serializers.simple import SimpleUserSerializer


class DietPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPhoto
        fields = ['id', 'owner', 'payment', 'photo']


class DietPaymentSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer(read_only=True)
    photos = DietPhotoSerializer(many=True)

    class Meta:
        model = DietPayment
        fields = ['id', 'owner', 'diet', 'type', 'liters', 'photos', 'amount', 'description']


class DietSerializer(serializers.ModelSerializer):
    payments = DietPaymentSerializer(many=True)

    class Meta:
        model = Diet
        fields = ['id', 'reservation', 'start', 'end', 'payments', 'completed', 'modified', 'number_of_diets']
