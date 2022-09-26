from rest_framework import serializers

from applications.diets.models import Diet, DietPayment


class PatchDietSerializer(serializers.ModelSerializer):

    class Meta:
        model = Diet
        fields = ('id', 'start', 'end', 'completed', 'number_of_diets')
        read_only_fields = ('id',)


class PatchPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPayment
        fields = ('id', 'type', 'liters', 'amount', 'description', 'demand')
        read_only_fields = ('id',)
