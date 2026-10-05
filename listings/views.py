import math

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.throttling import (
    AnonRateThrottle,
    ScopedRateThrottle,
    UserRateThrottle,
)
from rest_framework.views import APIView

from .models import Business, Category, ClaimRequest, Review, VerificationLog
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    BusinessSerializer,
    CategorySerializer,
    ClaimCreateSerializer,
    ClaimRequestSerializer,
    RegisterSerializer,
    ReviewSerializer,
)


class ClaimThrottle(UserRateThrottle):
    scope = "claims"  # rate comes from DEFAULT_THROTTLE_RATES["claims"] in settings


class RegisterThrottle(AnonRateThrottle):
    scope = "register"  # rate comes from DEFAULT_THROTTLE_RATES["register"]


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


class RegisterView(generics.CreateAPIView):
    """Public signup. Throttled by client IP via the 'register' scope."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"id": user.id, "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "owner", "is_verified", "status"]
    search_fields = ["name", "address"]

    def perform_create(self, serializer):
        # A listing created by a logged-in user is theirs from the start,
        # so it must not be open to ownership claims.
        serializer.save(owner=self.request.user, status=Business.Status.CLAIMED)

    # --- Verification (staff only) --------------------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser],
            url_path="verify")
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
        return Response(
            {"status": "verified", "business_id": business.id},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser],
            url_path="unverify")
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
        return Response(
            {"status": "unverified", "business_id": business.id},
            status=status.HTTP_200_OK,
        )

        # --- Discovery -------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="nearby",
            permission_classes=[IsAuthenticatedOrReadOnly])
    def nearby(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius_km = request.query_params.get("radius_km", 5)

        if lat is None or lng is None:
            return Response(
                {"detail": "lat and lng query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            lat, lng, radius_km = float(lat), float(lng), float(radius_km)
        except ValueError:
            return Response(
                {"detail": "lat, lng, and radius_km must be numbers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        candidates = Business.objects.filter(
            latitude__isnull=False, longitude__isnull=False
        )
        results = []
        for business in candidates:
            distance = haversine_km(
                lat, lng, business.latitude, business.longitude
            )
            if distance <= radius_km:
                results.append((distance, business))
        # verified first, then nearest first within each group
        results.sort(key=lambda pair: (not pair[1].is_verified, pair[0]))

        serialized = []
        for distance, business in results:
            data = BusinessSerializer(business).data
            data["distance_km"] = round(distance, 2)
            serialized.append(data)
        return Response({"count": len(serialized), "results": serialized})


    # --- Claims (any authenticated user) ---------------------------------
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated],
            throttle_classes=[ClaimThrottle])
    def claim(self, request, pk=None):
        business = self.get_object()
        if business.status != Business.Status.UNCLAIMED:
            return Response(
                {"detail": "This listing has already been claimed."},
                status=status.HTTP_409_CONFLICT,
            )
        serializer = ClaimCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            claim = ClaimRequest.objects.create(
                business=business,
                claimant=request.user,
                **serializer.validated_data,
            )
        except IntegrityError:
            return Response(
                {"detail": "You already have a pending claim for this listing."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            ClaimRequestSerializer(claim).data, status=status.HTTP_201_CREATED
        )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "reviews"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ClaimReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """Staff only: list pending claims, approve or reject them."""

    serializer_class = ClaimRequestSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = ClaimRequest.objects.select_related(
            "business", "claimant", "reviewed_by"
        )
        if self.action == "list":
            qs = qs.filter(state=ClaimRequest.State.PENDING)
        return qs.order_by("created_at")

    def _review(self, request, pk, approve):
        with transaction.atomic():
            claim = get_object_or_404(
                ClaimRequest.objects.select_for_update().select_related("business"),
                pk=pk,
            )
            if claim.state != ClaimRequest.State.PENDING:
                return Response(
                    {"detail": "This claim has already been reviewed."},
                    status=status.HTTP_409_CONFLICT,
                )
            now = timezone.now()
            note = str(request.data.get("note", ""))[:500]

            if approve:
                business = claim.business
                if business.status != Business.Status.UNCLAIMED:
                    return Response(
                        {"detail": "Listing is no longer unclaimed."},
                        status=status.HTTP_409_CONFLICT,
                    )
                business.owner = claim.claimant
                business.status = Business.Status.CLAIMED
                business.save(update_fields=["owner", "status", "updated_at"])
                # one approval closes every other pending claim on this listing
                ClaimRequest.objects.filter(
                    business=business, state=ClaimRequest.State.PENDING
                ).exclude(pk=claim.pk).update(
                    state=ClaimRequest.State.REJECTED,
                    reviewed_by=request.user,
                    reviewed_at=now,
                    review_note="Another claim was approved for this listing.",
                )

            claim.state = (
                ClaimRequest.State.APPROVED if approve
                else ClaimRequest.State.REJECTED
            )
            claim.reviewed_by = request.user
            claim.reviewed_at = now
            claim.review_note = note
            claim.save()

        return Response(ClaimRequestSerializer(claim).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._review(request, pk, approve=True)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._review(request, pk, approve=False)


class MyClaimsView(generics.ListAPIView):
    """A logged-in user's own claim requests."""
    serializer_class = ClaimRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (ClaimRequest.objects.filter(claimant=self.request.user)
                .select_related("business").order_by("-created_at"))


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({"id": user.id, "username": user.username,
                         "email": user.email, "is_staff": user.is_staff})