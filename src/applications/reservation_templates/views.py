from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from applications.reservation_templates.serializers.create import ReservationTemplateSerializer
from applications.reservation_templates.services.queryset import get_reservation_templates_queryset
from shared.permissions import ONLY_ADMIN_OR_SUPER_ADMIN, ONLY_AUTHENTICATED


class ReservationTemplateViewSet(viewsets.ViewSet):

    @swagger_auto_schema(responses={200: ReservationTemplateSerializer(many=True)})
    def list(self, request):
        """
        List reservation templates.
        """
        requester = self.request.user
        queryset = get_reservation_templates_queryset(requester)
        serializer = ReservationTemplateSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: ReservationTemplateSerializer()})
    def retrieve(self, request, pk=None):
        """
        Retrieve a reservation template.
        """
        requester = self.request.user
        queryset = get_reservation_templates_queryset(requester)
        template = get_object_or_404(queryset, pk=pk)
        serializer = ReservationTemplateSerializer(template)
        return Response(serializer.data)

    @swagger_auto_schema(responses={201: ReservationTemplateSerializer()})
    def create(self, request):
        """
        Create a reservation template.
        """
        tenant = self.request.user.tenant
        serializer = ReservationTemplateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=tenant)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: ReservationTemplateSerializer()})
    def update(self, request, pk=None):
        """
        Update a reservation template.
        """
        requester = self.request.user
        queryset = get_reservation_templates_queryset(requester)
        template = get_object_or_404(queryset, pk=pk)
        serializer = ReservationTemplateSerializer(template, self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=requester.tenant)
        return Response(serializer.data)

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        """
        Destroy a reservation template.
        """
        requester = self.request.user
        queryset = get_reservation_templates_queryset(requester)
        template = get_object_or_404(queryset, pk=pk)
        template.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        elif self.action in ['list', 'retrieve']:
            permission_classes = ONLY_AUTHENTICATED
        # If new endpoints are added, by default add them to ONLY ADMIN
        else:
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        return [permission() for permission in permission_classes]