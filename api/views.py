from .models import VehicleType, Vehicle
from .serializers import VehicleTypeSerializer, VehicleSerializer, CreateVehicleSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics


# GET: List all vehicles
class VehicleList(generics.ListAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


# POST: Create one vehicle
class CreateVehicle(generics.CreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = CreateVehicleSerializer


# GET: List all vehicles types
class VehicleTypeList(generics.ListAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer


# POST: Create one vehicle type
class CreateVehicleType(generics.CreateAPIView):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer



"""
@api_view(['GET', 'POST'])
def vehicle_type_list(request):

    if request.method == 'GET':
        types = VehicleType.objects.all()
        serializer = VehicleTypeSerializer(types, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = VehicleTypeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def vehicle_type_detail(request, pk):
    # Retrieve, update or delete a vehicle type.

    try:
        vehicle_type = VehicleType.objects.get(pk=pk)
    except VehicleType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Object found and stored in vehicle_type variable

    if request.method == 'GET':
        serializer = VehicleTypeSerializer(vehicle_type)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = VehicleTypeSerializer(vehicle_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        vehicle_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""