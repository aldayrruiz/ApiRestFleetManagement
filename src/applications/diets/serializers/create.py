from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from applications.diets.models.diet import Diet, DietPhoto, DietCollection
from applications.diets.serializers.simple import DietSerializer


class CreateDietCollectionSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    completed = serializers.ReadOnlyField(default=False)
    diets = DietSerializer(read_only=True, many=True)

    class Meta:
        model = DietCollection
        fields = ['id', 'reservation', 'start', 'end', 'owner', 'diets', 'completed']


class CreateDietSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Diet
        fields = ['id', 'owner', 'collection', 'type', 'liters', 'amount', 'description']


class CreateDietPhotoSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    photo = Base64ImageField(required=False)

    class Meta:
        model = DietPhoto
        fields = ['id', 'owner', 'diet', 'photo']
