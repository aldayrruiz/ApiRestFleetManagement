from django.urls import path
from . import views

urlpatterns = [
    path('create/vehicle/', views.CreateVehicle.as_view()),
    path('list/vehicle/', views.VehicleList.as_view()),
    path('create/vehicletype/', views.CreateVehicleType.as_view()),
    path('list/vehicletype/', views.VehicleTypeList.as_view()),
]

#path('list/vehicletypes', views.vehicle_type_list),
#path('vehicle_type/<uuid:pk>/', views.vehicle_type_detail),
