from rest_framework.routers import DefaultRouter

from incidents.views import IncidentViewSet

router = DefaultRouter()

router.register(r'', IncidentViewSet, basename='incidents')

urlpatterns = router.urls
