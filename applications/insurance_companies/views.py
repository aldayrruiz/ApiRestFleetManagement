from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from applications.insurance_companies.serializers.create import InsuranceCompanySerializer
from applications.insurance_companies.services.queryset import get_insurance_companies_queryset
from shared.permissions import ONLY_ADMIN, ONLY_AUTHENTICATED


class InsuranceCompanyViewSet(viewsets.ViewSet):

    @swagger_auto_schema(responses={200: InsuranceCompanySerializer(many=True)})
    def list(self, request):
        """
        List insurance companies
        """
        requester = self.request.user
        queryset = get_insurance_companies_queryset(requester)
        serializer = InsuranceCompanySerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: InsuranceCompanySerializer()})
    def retrieve(self, request, pk=None):
        requester = self.request.user
        queryset = get_insurance_companies_queryset(requester)
        insurance_company = get_object_or_404(queryset, pk=pk)
        serializer = InsuranceCompanySerializer(insurance_company)
        return Response(serializer.data)

    @swagger_auto_schema(responses={201: InsuranceCompanySerializer()})
    def create(self, request):
        tenant = self.request.user.tenant
        serializer = InsuranceCompanySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=tenant)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: InsuranceCompanySerializer()})
    def update(self, request, pk=None):
        requester = self.request.user
        queryset = get_insurance_companies_queryset(requester)
        insurance_company = get_object_or_404(queryset, pk=pk)
        serializer = InsuranceCompanySerializer(insurance_company, self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=requester.tenant)
        return Response(serializer.data)

    @swagger_auto_schema()
    def destroy(self, request, pk=None):
        requester = self.request.user
        queryset = get_insurance_companies_queryset(requester)
        insurance_company = get_object_or_404(queryset, pk=pk)
        insurance_company.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = ONLY_ADMIN
        elif self.action in ['list', 'retrieve']:
            permission_classes = ONLY_AUTHENTICATED
        # If new endpoints are added, by default add them to ONLY ADMIN
        else:
            permission_classes = ONLY_ADMIN
        return [permission() for permission in permission_classes]
