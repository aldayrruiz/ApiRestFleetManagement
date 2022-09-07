from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from applications.diets.exceptions.completed_collection import CompletedDietCollectionError
from applications.diets.models.diet import DietCollection, DietPhoto
from applications.diets.serializers.create import CreateDietCollectionSerializer, CreateDietSerializer, \
    CreateDietPhotoSerializer
from applications.diets.serializers.simple import DietCollectionSerializer, DietSerializer
from applications.diets.serializers.update import PatchDietCollectionSerializer, PatchDietSerializer
from applications.diets.services.queryset import get_diet_collection_queryset, get_diet_queryset
from applications.reservations.models import Reservation
from applications.users.models import User
from utils.api.query import query_str


class DietCollectionViewSet(viewsets.ViewSet):

    @swagger_auto_schema(request_body=CreateDietCollectionSerializer, responses={200: CreateDietCollectionSerializer()})
    def create(self, request):
        requester = self.request.user
        serializer = CreateDietCollectionSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=requester.tenant)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: DietCollectionSerializer()})
    @action(detail=False, methods=['get'])
    def get_collection_by_reservation(self, request):
        reservation_id = query_str(request, 'reservationId', required=True)
        try:
            collection = Reservation.objects.get(id=reservation_id).diet_collection
        except DietCollection.DoesNotExist:
            raise NotFound('Diet collection not found.')
        serializer = DietCollectionSerializer(collection)
        return Response(serializer.data)

    @swagger_auto_schema(responses={200: PatchDietCollectionSerializer()})
    def partial_update(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_collection_queryset(requester)
        collection = get_object_or_404(queryset, pk=pk)
        if collection.completed:
            raise CompletedDietCollectionError()
        collection.modified = True
        serializer = PatchDietCollectionSerializer(collection, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DietViewSet(viewsets.ViewSet):

    def create(self, request):
        requester = self.request.user
        serializer = CreateDietSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        diet = serializer.save(tenant=requester.tenant)
        collection = diet.collection
        collection.modified = True
        collection.save()
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_queryset(requester)
        diet = get_object_or_404(queryset, pk=pk)
        serializer = DietSerializer(diet)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_queryset(requester)
        diet = get_object_or_404(queryset, pk=pk)
        if diet.collection.completed:
            raise CompletedDietCollectionError()
        serializer = PatchDietSerializer(diet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        requester = self.request.user
        queryset = get_diet_queryset(requester)
        diet = get_object_or_404(queryset, pk=pk)
        if diet.collection.completed:
            raise CompletedDietCollectionError()
        diet.delete()
        return Response(status=HTTP_204_NO_CONTENT)


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
        if photo.diet.collection.completed:
            raise CompletedDietCollectionError()
        photo.delete()
        return Response(status=HTTP_204_NO_CONTENT)
