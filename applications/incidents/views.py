from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from applications.incidents.models import Incident
from applications.incidents.serializers.create import CreateIncidentSerializer
from applications.incidents.serializers.simple import SimpleIncidentSerializer
from applications.users.models import Role
from applications.users.services import get_admin
from shared.permissions import IsOwnerReservationOrAdmin
from utils.email.incidents import send_created_incident_email


class IncidentViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        If take_all is True and requester is admin, it will return all incidents.
        Otherwise, it will return only the requester incidents.
        :param request:
        :return:
        """
        take_all = bool(self.request.query_params.get('take_all'))
        requester = self.request.user
        if requester.role == Role.ADMIN and take_all is True:
            queryset = Incident.objects.all()
        else:
            queryset = Incident.objects.filter(owner=requester)
        serializer = SimpleIncidentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        serializer = CreateIncidentSerializer(data=self.request.data)

        if serializer.is_valid():
            incident = serializer.save(owner=user)
            send_created_incident_email(get_admin(), incident)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = self.request.user
        queryset = Incident.objects.filter(owner=user)
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
            permission_classes = [permissions.IsAuthenticated, IsOwnerReservationOrAdmin]
        else:
            # You must be authenticated and have access to the vehicle.
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
