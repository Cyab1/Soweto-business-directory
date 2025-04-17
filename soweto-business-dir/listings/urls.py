from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BusinessViewSet, ReviewViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r"categories", CategoryViewSet)
router.register(r"businesses", BusinessViewSet)
router.register(r"reviews", ReviewViewSet)

# Define URL patterns
urlpatterns = [
    path("", include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwagerView.as_view(url_name='schema')) 
]
