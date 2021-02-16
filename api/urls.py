from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserList.as_view()),
    path('vehicles/', views.VehicleList.as_view()),
    path('vehicletypes/', views.VehicleTypeList.as_view()),
    path('reservations/', views.ReservationList.as_view()),

    path('vehicles/<uuid:pk>/', views.VehicleDetail.as_view()),
    path('vehicletypes/<uuid:pk>/', views.VehicleTypeDetail.as_view()),
    path('reservations/<uuid:pk>/', views.ReservationDetail.as_view()),
]
