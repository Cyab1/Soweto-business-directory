import math

from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from .models import Business, Category, Review, VerificationLog
from .serializers import BusinessSerializer, CategorySerializer, ReviewSerializer
from .permissions import IsOwnerOrReadOnly


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "owner", "is_verified"]
    search_fields = ["name", "address"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser], url_path="verify")
    def verify(self, request, pk=None):
        business = self.get_object()
        business.is_verified = True
        business.verified_by = request.user
        business.verified_at = timezone.now()
        business.save()
        VerificationLog.objects.create(
            business=business, action="verified", performed_by=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response({"status": "verified", "business_id": business.id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser], url_path="unverify")
    def unverify(self, request, pk=None):
        business = self.get_object()
        business.is_verified = False
        business.verified_by = None
        business.verified_at = None
        business.save()
        VerificationLog.objects.create(
            business=business, action="unverified", performed_by=request.user,
            notes=request.data.get("notes", ""),
        )
        return Response({"status": "unverified", "business_id": business.id}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="nearby", permission_classes=[IsAuthenticatedOrReadOnly])
    def nearby(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = request.query_params.get("radius_km", 5)

        if lat is None or lng is None:
            return Response({"detail": "lat and lng query parameters are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lat, lng, radius_km = float(lat), float(lng), float(radius_km)
        except ValueError:
            return Response({"detail": "lat, lng, and radius_km must be numbers."}, status=status.HTTP_400_BAD_REQUEST)

        candidates = Business.objects.filter(is_verified=True, latitude__isnull=False, longitude__isnull=False)
        results = []
        for business in candidates:
            distance = haversine_km(lat, lng, business.latitude, business.longitude)
            if distance <= radius_km:
                results.append((distance, business))
        results.sort(key=lambda pair: pair[0])

        serialized = []
        for distance, business in results:
            data = BusinessSerializer(business).data
            data["distance_km"] = round(distance, 2)
            serialized.append(data)
        return Response({"count": len(serialized), "results": serialized})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "reviews"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)