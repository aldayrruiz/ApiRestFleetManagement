from rest_framework import serializers

from applications.reports.models.monthly import MonthlyReport


class SimpleReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonthlyReport
        fields = ['id', 'month', 'year']
