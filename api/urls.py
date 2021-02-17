from django.urls import path
from . import views

urlpatterns = [
    path('list/user/', views.UserList.as_view()),
    path('list/vehicle/', views.VehicleList.as_view()),
    path('list/vehicletype/', views.VehicleTypeList.as_view()),
    path('list/reservation/', views.ReservationList.as_view()),

    path('detail/vehicle/<uuid:pk>/', views.VehicleDetail.as_view()),
    path('detail/vehicletype/<uuid:pk>/', views.VehicleTypeDetail.as_view()),
    path('detail/reservation/<uuid:pk>/', views.ReservationDetail.as_view()),

    path('create/vehicle/', views.VehicleCreate.as_view()),
    path('create/vehicletype/', views.VehicleTypeCreate.as_view()),
    path('create/reservation/', views.ReservationCreate.as_view()),
]
