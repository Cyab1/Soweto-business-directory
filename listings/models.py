from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Business(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    contact_info = models.CharField(max_length=200)
    services = models.TextField()
    image = models.ImageField(upload_to="business_image/", null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # --- Verification fields ---
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_businesses",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.business.name}"


class VerificationLog(models.Model):
    """Immutable audit trail of every verification action taken on a Business."""

    ACTION_CHOICES = [
        ("verified", "Verified"),
        ("unverified", "Unverified"),
        ("rejected", "Rejected"),
    ]

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="verification_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — {self.business.name} by {self.performed_by.username}"