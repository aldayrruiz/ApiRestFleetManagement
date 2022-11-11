from rest_framework import serializers

from applications.diets.models import DietMonthlyPdfReport


class SimpleTenantBillingMonthlyPdfReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietMonthlyPdfReport
        fields = ['id', 'month', 'year']
