import logging

from rest_framework import permissions, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from applications.incidents.serializers.create import CreateIncidentSerializer
from applications.incidents.serializers.simple import SimpleIncidentSerializer
from applications.incidents.services.queryset import get_incident_queryset
from applications.users.services.search import get_admin
from shared.permissions import IsOwnerReservationOrAdmin, IsNotDisabled
from utils.api.query import query_bool
from utils.email.incidents import send_created_incident_email

logger = logging.getLogger(__name__)


class IncidentViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is True and requester is admin, it will return all incidents.
        Otherwise, it will return only the requester incidents.
        :param request:
        :return:
        """
        take_all = query_bool(self.request, 'takeAll')
        logger.info('List incidents request received. [takeAll: {}]'.format(take_all))
        requester = self.request.user
        queryset = get_incident_queryset(requester, take_all)
        serializer = SimpleIncidentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        logger.info('Create incident request received.')
        requester = self.request.user
        tenant = requester.tenant
        serializer = CreateIncidentSerializer(data=self.request.data)

        if not serializer.is_valid():
            log_error_serializing(serializer)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        incident = serializer.save(owner=requester, tenant=tenant)
        send_created_incident_email(get_admin(tenant), incident)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        logger.info('Retrieve incident request received.')
        requester = self.request.user
        queryset = get_incident_queryset(requester, take_all=True)
        incident = get_object_or_404(queryset, pk=pk)
        serializer = SimpleIncidentSerializer(incident)
        return Response(serializer.data)

    # THIS RESTRICT TO REQUESTER CREATE AN INCIDENT OF RESERVATION WHICH IS NOT OWNER.
    # IF REQUESTER IS ADMIN, HE CAN CREATE AN INCIDENT EVEN IF HE IS NOT OWNER.
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled, IsOwnerReservationOrAdmin]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled]
        return [permission() for permission in permission_classes]


def log_error_serializing(serializer):
    logger.error("Incident couldn't be serialized with {} because of {}."
                 .format(serializer.__class__.__name__, serializer.errors))
