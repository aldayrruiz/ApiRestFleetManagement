from rest_framework import serializers

from applications.diets.models.diet import DietCollection, Diet


class PatchDietCollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietCollection
        fields = ('id', 'start', 'end', 'completed')
        read_only_fields = ('id',)


class PatchDietSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diet
        fields = ('id', 'type', 'liters', 'amount', 'description')
        read_only_fields = ('id',)
