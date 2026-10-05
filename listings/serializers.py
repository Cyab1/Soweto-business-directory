from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Business, Category, ClaimRequest, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class BusinessSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Business
        fields = "__all__"
        read_only_fields = [
            "owner",
            "status",
            "source",
            "external_id",
            "is_verified",
            "verified_by",
            "verified_at",
            "created_at",
            "updated_at",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


# --- Claims ---------------------------------------------------------------

class ClaimCreateSerializer(serializers.ModelSerializer):
    """POST body for a user submitting a new claim on a business."""

    class Meta:
        model = ClaimRequest
        fields = ["evidence", "contact_phone"]

    def validate_evidence(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError(
                "Please explain how you can prove you own this business."
            )
        return value

    def validate_contact_phone(self, value):
        value = value.strip()
        if len(value) < 7:
            raise serializers.ValidationError("Enter a valid contact phone number.")
        return value


class ClaimRequestSerializer(serializers.ModelSerializer):
    """Read-only representation of a claim, for admin and 'my claims' views."""

    business_name = serializers.CharField(source="business.name", read_only=True)
    claimant_username = serializers.CharField(
        source="claimant.username", read_only=True
    )
    reviewed_by_username = serializers.CharField(
        source="reviewed_by.username", read_only=True, default=None
    )

    class Meta:
        model = ClaimRequest
        fields = [
            "id",
            "business",
            "business_name",
            "claimant",
            "claimant_username",
            "evidence",
            "contact_phone",
            "state",
            "created_at",
            "reviewed_by",
            "reviewed_by_username",
            "reviewed_at",
            "review_note",
        ]
        read_only_fields = [
            "id",
            "business",
            "business_name",
            "claimant",
            "claimant_username",
            "evidence",
            "contact_phone",
            "state",
            "created_at",
            "reviewed_by",
            "reviewed_by_username",
            "reviewed_at",
            "review_note",
        ]


class ClaimReviewSerializer(serializers.Serializer):
    """Input for an admin approving or rejecting a claim."""

    action = serializers.ChoiceField(choices=["approve", "reject"])
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_note(self, value):
        return value.strip()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"email": {"required": True}}

    def validate_email(self, value):
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        candidate = get_user_model()(username=attrs["username"], email=attrs["email"])
        validate_password(attrs["password"], candidate)  # runs your AUTH_PASSWORD_VALIDATORS
        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)