from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from applications.maintenance.models import CleaningCard
from applications.maintenance.serializers.cleaning.card import CleaningCardSerializer


class CleaningCardViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=CleaningCardSerializer, responses={200: CleaningCardSerializer()})
    def create(self, request):
        serializer = CleaningCardSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CleaningCardSerializer, responses={200: CleaningCardSerializer()})
    def update(self, request, pk=None):
        queryset = CleaningCard.objects.all()
        card = get_object_or_404(queryset, pk=pk)
        serializer = CleaningCardSerializer(card, data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
