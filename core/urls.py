from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, DealViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"deals", DealViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
