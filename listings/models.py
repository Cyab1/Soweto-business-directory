from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Business(models.Model):
    class Status(models.TextChoices):
        UNCLAIMED = "unclaimed", "Unclaimed"
        CLAIMED = "claimed", "Claimed"

    class PriceRange(models.TextChoices):
        LOW = "$", "Budget"
        MID = "$$", "Mid-range"
        HIGH = "$$$", "Premium"

    # --- Core identity -------------------------------------------------
    name = models.CharField(max_length=200)

    # owner is now optional: imported listings have no owner until claimed
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="businesses",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="businesses",
    )

    address = models.CharField(max_length=200)
    contact_info = models.CharField(max_length=200, blank=True, default="")
    services = models.TextField(blank=True, default="")

    image = models.ImageField(upload_to="business_image/", null=True, blank=True)
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # --- Extended contact / links --------------------------------------
    price_range = models.CharField(
        max_length=3, choices=PriceRange.choices, blank=True, default=""
    )
    whatsapp = models.CharField(max_length=20, blank=True, default="")
    website_url = models.URLField(blank=True, default="")
    booking_url = models.URLField(blank=True, default="")
    instagram = models.CharField(max_length=100, blank=True, default="")
    facebook = models.CharField(max_length=100, blank=True, default="")

    # --- Provenance / claim state --------------------------------------
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.UNCLAIMED
    )
    source = models.CharField(max_length=50, blank=True, default="")  # e.g. "digismart_import"
    external_id = models.CharField(max_length=100, blank=True, default="", db_index=True)

    # --- Verification ---------------------------------------------------
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_businesses",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["category", "status"]),
        ]
        constraints = [
            # One row per upstream record; blank pairs are exempt so manual
            # entries and un-imported businesses don't collide.
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=~Q(source="") & ~Q(external_id=""),
                name="uniq_business_source_external_id",
            ),
        ]

    def __str__(self):
        return self.name

    # --- Convenience helpers -------------------------------------------
    @property
    def is_claimed(self):
        return self.owner_id is not None

    def claim(self, user):
        """Attach an owner. Refuses to steal an already-claimed listing."""
        if self.owner_id is not None and self.owner_id != user.pk:
            raise ValueError("This business has already been claimed.")
        self.owner = user
        self.status = self.Status.CLAIMED
        self.save(update_fields=["owner", "status", "updated_at"])

    def mark_verified(self, by, notes=""):
        self.is_verified = True
        self.verified_by = by
        self.verified_at = timezone.now()
        self.save(
            update_fields=["is_verified", "verified_by", "verified_at", "updated_at"]
        )
        return VerificationLog.objects.create(
            business=self, action="verified", performed_by=by, notes=notes
        )

    def mark_unverified(self, by, notes=""):
        self.is_verified = False
        self.verified_by = None
        self.verified_at = None
        self.save(
            update_fields=["is_verified", "verified_by", "verified_at", "updated_at"]
        )
        return VerificationLog.objects.create(
            business=self, action="unverified", performed_by=by, notes=notes
        )

    @transaction.atomic
    def approve_claim(self, claim, reviewer, note=""):
        """Approve a ClaimRequest: transfer ownership and mark the claim reviewed."""
        if claim.business_id != self.pk:
            raise ValueError("Claim does not belong to this business.")
        if claim.state != ClaimRequest.State.PENDING:
            raise ValueError("Only pending claims can be approved.")

        # Lock this business row so two admins can't race the same claim.
        Business.objects.select_for_update().get(pk=self.pk)

        if self.owner_id is not None and self.owner_id != claim.claimant_id:
            raise ValueError("This business already has a different owner.")

        self.owner = claim.claimant
        self.status = self.Status.CLAIMED
        self.save(update_fields=["owner", "status", "updated_at"])

        claim.state = ClaimRequest.State.APPROVED
        claim.reviewed_by = reviewer
        claim.reviewed_at = timezone.now()
        claim.review_note = note
        claim.save(
            update_fields=["state", "reviewed_by", "reviewed_at", "review_note"]
        )

        # Auto-reject any other pending claims on this business.
        ClaimRequest.objects.filter(
            business=self, state=ClaimRequest.State.PENDING
        ).exclude(pk=claim.pk).update(
            state=ClaimRequest.State.REJECTED,
            reviewed_by=reviewer,
            reviewed_at=timezone.now(),
            review_note="Another claim was approved first.",
        )

        return claim

    @transaction.atomic
    def reject_claim(self, claim, reviewer, note=""):
        if claim.business_id != self.pk:
            raise ValueError("Claim does not belong to this business.")
        if claim.state != ClaimRequest.State.PENDING:
            raise ValueError("Only pending claims can be rejected.")

        claim.state = ClaimRequest.State.REJECTED
        claim.reviewed_by = reviewer
        claim.reviewed_at = timezone.now()
        claim.review_note = note
        claim.save(
            update_fields=["state", "reviewed_by", "reviewed_at", "review_note"]
        )
        return claim


class Review(models.Model):
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "user"], name="uniq_review_per_user_per_business"
            ),
        ]

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
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} — {self.business.name} by {self.performed_by.username}"


class ClaimRequest(models.Model):
    """A user's request to take ownership of a (typically imported) Business."""

    class State(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="claims"
    )
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="claims",
    )
    evidence = models.TextField(
        help_text="How can we confirm you own this business?"
    )
    contact_phone = models.CharField(max_length=20)
    state = models.CharField(
        max_length=10, choices=State.choices, default=State.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["business", "state"]),
            models.Index(fields=["claimant", "state"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["business", "claimant"],
                condition=models.Q(state="pending"),
                name="one_pending_claim_per_user_per_business",
            )
        ]

    def __str__(self):
        return (
            f"Claim by {self.claimant.username} "
            f"on {self.business.name} [{self.state}]"
        )

    @property
    def is_pending(self):
        return self.state == self.State.PENDING