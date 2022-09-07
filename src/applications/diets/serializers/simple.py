from rest_framework import serializers

from applications.diets.models.diet import Diet, DietPhoto, DietCollection
from applications.users.serializers.simple import SimpleUserSerializer


class DietPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPhoto
        fields = ['id', 'owner', 'diet', 'photo']


class DietSerializer(serializers.ModelSerializer):
    owner = SimpleUserSerializer(read_only=True)
    photos = DietPhotoSerializer(many=True)

    class Meta:
        model = Diet
        fields = ['id', 'owner', 'collection', 'type', 'liters', 'photos', 'amount', 'description']


class DietCollectionSerializer(serializers.ModelSerializer):
    diets = DietSerializer(many=True)

    class Meta:
        model = DietCollection
        fields = ['id', 'reservation', 'start', 'end', 'diets', 'completed', 'modified']
