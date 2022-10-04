import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from applications.incidents.serializers.create import CreateIncidentSerializer
from applications.incidents.serializers.simple import SimpleIncidentSerializer
from applications.incidents.serializers.special import SolveIncidentSerializer
from applications.incidents.services.emails.created import IncidentCreatedEmail
from applications.incidents.services.queryset import get_incident_queryset
from applications.incidents.services.solver import IncidentSolver
from shared.permissions import IsOwnerReservationOrAdmin, IsNotDisabled, ONLY_ADMIN_OR_SUPER_ADMIN, ONLY_AUTHENTICATED
from utils.api.query import query_bool

logger = logging.getLogger(__name__)


class IncidentViewSet(viewsets.ViewSet):

    @swagger_auto_schema(responses={200: SimpleIncidentSerializer(many=True)})
    def list(self, request):
        """
        List own incidents. If takeAll is given, it lists all incidents from everyone.
        """
        take_all = query_bool(self.request, 'takeAll')
        logger.info('List incidents request received. [takeAll: {}]'.format(take_all))
        requester = self.request.user
        queryset = get_incident_queryset(requester, take_all)
        serializer = SimpleIncidentSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: SimpleIncidentSerializer()})
    def retrieve(self, request, pk=None):
        """
        Retrieve an incident.
        """
        logger.info('Retrieve incident request received.')
        requester = self.request.user
        queryset = get_incident_queryset(requester, take_all=True)
        incident = get_object_or_404(queryset, pk=pk)
        serializer = SimpleIncidentSerializer(incident)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=CreateIncidentSerializer, responses={201: CreateIncidentSerializer()})
    def create(self, request):
        """
        Create an incident.
        """
        logger.info('Create incident request received.')
        requester = self.request.user
        tenant = requester.tenant
        serializer = CreateIncidentSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        incident = serializer.save(owner=requester, tenant=tenant)
        IncidentCreatedEmail(incident).send()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def solve(self, request, pk=None):
        """
        Mark incident as solved
        """
        requester = self.request.user
        queryset = get_incident_queryset(requester, take_all=True)
        incident = get_object_or_404(queryset, pk=pk)

        # Save solver & send emails
        solver = IncidentSolver(incident)
        solver.solve(solver=requester)

        # Save solver message
        serializer = SolveIncidentSerializer(incident, self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_200_OK)

    # THIS RESTRICTS TO REQUESTER CREATE AN INCIDENT OF RESERVATION WHICH IS NOT OWNER.
    # IF REQUESTER IS ADMIN, HE CAN CREATE AN INCIDENT EVEN IF HE IS NOT OWNER.
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'solve':
            permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsNotDisabled, IsOwnerReservationOrAdmin]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = ONLY_AUTHENTICATED
        return [permission() for permission in permission_classes]
