from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from applications.maintenance.serializers.odometer.card import OdometerCardSerializer
from shared.permissions import ONLY_ADMIN_OR_SUPER_ADMIN, ONLY_AUTHENTICATED


class OdometerCardViewSet(viewsets.ViewSet):
    @swagger_auto_schema(request_body=OdometerCardSerializer, responses={200: OdometerCardSerializer()})
    def create(self, request):
        serializer = OdometerCardSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: OdometerCardSerializer()})
    @action(detail=False, methods=['get'])
    def get(self, request):
        requester = self.request.user
        try:
            card = requester.tenant.odometer_card
        except:
            return Response(status=404)
        serializer = OdometerCardSerializer(card, context={'request': self.request})
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OdometerCardSerializer, responses={200: OdometerCardSerializer()})
    def update(self, request, pk=None):
        requester = self.request.user
        card = requester.tenant.odometer_card
        if not card:
            return Response(status=404)
        serializer = OdometerCardSerializer(card, data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['create', 'update']:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        elif self.action in ['get']:
            permission_classes = ONLY_AUTHENTICATED
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]

