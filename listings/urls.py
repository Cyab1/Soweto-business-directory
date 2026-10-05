from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BusinessViewSet,
    CategoryViewSet,
    ClaimReviewViewSet,
    ReviewViewSet,
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"businesses", BusinessViewSet)
router.register(r"reviews", ReviewViewSet)
router.register(r"claims", ClaimReviewViewSet, basename="claim")

urlpatterns = [
    path("", include(router.urls)),  # Include all routes from the router
]