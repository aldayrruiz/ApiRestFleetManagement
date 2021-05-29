from django.urls import re_path, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, AdminAuthToken, RegistrationViewSet

router = DefaultRouter()

router.register(r'', UserViewSet, basename='user')
router.register(r'register', RegistrationViewSet, basename='register')

urlpatterns = router.urls

urlpatterns += [
    re_path(r'^login/?$', obtain_auth_token, name='login'),
    path('api/admin/login/', AdminAuthToken.as_view())
]
