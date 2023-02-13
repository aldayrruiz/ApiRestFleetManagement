from django.http import FileResponse, Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from applications.diets.exceptions.completed_diet import CompletedDietError
from applications.diets.models import Diet
from applications.diets.serializers.create import CreateDietSerializer, CreateDietPaymentSerializer, \
    CreateDietPhotoSerializer
from applications.diets.serializers.report import SimpleDietMonthlyPdfReportSerializer
from applications.diets.serializers.simple import DietSerializer, DietPaymentSerializer
from applications.diets.serializers.update import PatchDietSerializer, PatchPaymentSerializer
from applications.diets.services.completer import DietUpdater
from applications.diets.services.queryset import get_diet_queryset, get_diet_payment_queryset, get_diet_reports_queryset
from applications.reservations.models import Reservation
from applications.users.models import User
from shared.permissions import ONLY_ADMIN_OR_SUPER_ADMIN, ONLY_AUTHENTICATED
from utils.api.query import query_str


class DietViewSet(viewsets.ViewSet):

    @swagger_auto_schema(request_body=CreateDietSerializer, responses={200: CreateDietSerializer()})
    def create(self, request):
        requester = self.request.user
        serializer = CreateDietSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=requester.tenant)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: DietSerializer()})
    @action(detail=False, methods=['get'])
    def get_diet_by_reservation(self, request):
        reservation_id = query_str(request, 'reservationId', required=True)
        try:
            diet = Reservation.objects.get(id=reservation_id).diet
        except Diet.DoesNotExist:
            raise NotFound('Diet not found.')
        serializer = DietSerializer(diet)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: PatchDietSerializer()})
    def partial_update(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_queryset(requester)
        diet = get_object_or_404(queryset, pk=pk)
        updater = DietUpdater(diet, self.request.data, requester)
        serializer = updater.update()
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in ['create', 'get_diet_by_reservation', 'partial_update']:
            permission_classes = ONLY_AUTHENTICATED
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]


class DietPaymentViewSet(viewsets.ViewSet):

    def create(self, request):
        requester = self.request.user
        serializer = CreateDietPaymentSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(tenant=requester.tenant)
        diet = payment.diet
        diet.modified = True
        diet.save()
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_payment_queryset(requester)
        payment = get_object_or_404(queryset, pk=pk)
        serializer = DietPaymentSerializer(payment)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_payment_queryset(requester)
        payment = get_object_or_404(queryset, pk=pk)
        if payment.diet.completed:
            raise CompletedDietError()
        serializer = PatchPaymentSerializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_payment_queryset(requester)
        payment = get_object_or_404(queryset, pk=pk)
        if payment.diet.completed:
            raise CompletedDietError()
        payment.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'partial_update', 'destroy']:
            permission_classes = ONLY_AUTHENTICATED
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]


class DietPhotoViewSet(viewsets.ViewSet):

    def create(self, request):
        requester = self.request.user
        serializer = CreateDietPhotoSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=requester.tenant)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        requester: User = self.request.user
        queryset = requester.diet_photos.all()
        photo = get_object_or_404(queryset, pk=pk)
        if photo.diet_payment.payments.completed:
            raise CompletedDietError()
        photo.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            permission_classes = ONLY_AUTHENTICATED
        else:
            raise Exception('The HTTP action {} is not supported'.format(self.action))
        return [permission() for permission in permission_classes]


class DietMonthlyPdfReportViewSet(viewsets.ViewSet):
    @swagger_auto_schema(responses={200: SimpleDietMonthlyPdfReportSerializer()})
    def list(self, request):
        """
        List monthly reports.
        """
        requester = self.request.user
        queryset = get_diet_reports_queryset(requester)
        print(queryset)
        serializer = SimpleDietMonthlyPdfReportSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def view(self, request, pk=None):
        """
        Return pdf file given its id.
        """
        requester = self.request.user
        queryset = get_diet_reports_queryset(requester)
        report = get_object_or_404(queryset, pk=pk)
        try:
            return FileResponse(open(report.pdf, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404()

    def get_permissions(self):
        permission_classes = ONLY_ADMIN_OR_SUPER_ADMIN
        return [permission() for permission in permission_classes]