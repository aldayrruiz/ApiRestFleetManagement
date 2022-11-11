from rest_framework import serializers

from applications.diets.models import DietMonthlyPdfReport


class SimpleDietMonthlyPdfReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietMonthlyPdfReport
        fields = ['id', 'month', 'year']
