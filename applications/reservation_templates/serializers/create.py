from rest_framework import serializers

from applications.reservation_templates.models import ReservationTemplate


class ReservationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationTemplate
        fields = ['id', 'title']
