from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

from .models import Business, Category, ClaimRequest

User = get_user_model()
API = "/api"
EVIDENCE = "I am the owner of this shop and can show my trading licence."


class ClaimFlowTests(APITestCase):
    def setUp(self):
        cache.clear()  # reset throttle counters between tests
        self.category = Category.objects.create(name="Test")
        self.owner = User.objects.create_user("owner1", password="Pass12345!")
        self.claimer = User.objects.create_user("claimer1", password="Pass12345!")
        self.claimer2 = User.objects.create_user("claimer2", password="Pass12345!")
        self.staff = User.objects.create_user("staff1", password="Pass12345!", is_staff=True)

        self.unclaimed = self.make_business("Unclaimed Shop", owner=None,
                                            status=Business.Status.UNCLAIMED)
        self.claimed = self.make_business("Claimed Shop", owner=self.owner,
                                          status=Business.Status.CLAIMED)

    def make_business(self, name, owner, status):
        return Business.objects.create(
            name=name, category=self.category, address="1 Test St",
            contact_info="0711111111", services="testing",
            owner=owner, status=status,
        )

    def claim(self, business, user=None, evidence=EVIDENCE):
        if user:
            self.client.force_authenticate(user)
        return self.client.post(
            f"{API}/businesses/{business.id}/claim/",
            {"evidence": evidence, "contact_phone": "0711111111"}, format="json")

    # ---- claiming ----
    def test_anonymous_cannot_claim(self):
        self.client.force_authenticate(None)
        response = self.claim(self.unclaimed)
        self.assertIn(response.status_code, (401, 403))

    def test_user_can_claim_unclaimed_listing(self):
        response = self.claim(self.unclaimed, self.claimer)
        self.assertEqual(response.status_code, 201)
        claim = ClaimRequest.objects.get()
        self.assertEqual(claim.claimant, self.claimer)
        self.assertEqual(claim.state, ClaimRequest.State.PENDING)

    def test_duplicate_pending_claim_is_rejected(self):
        self.claim(self.unclaimed, self.claimer)
        self.assertEqual(self.claim(self.unclaimed).status_code, 409)

    def test_cannot_claim_already_claimed_listing(self):
        self.assertEqual(self.claim(self.claimed, self.claimer).status_code, 409)

    def test_weak_evidence_is_rejected(self):
        self.assertEqual(self.claim(self.unclaimed, self.claimer, evidence="mine").status_code, 400)

    # ---- staff review ----
    def test_non_staff_cannot_list_or_approve(self):
        self.claim(self.unclaimed, self.claimer)
        claim = ClaimRequest.objects.get()
        self.assertEqual(self.client.get(f"{API}/claims/").status_code, 403)
        self.assertEqual(self.client.post(f"{API}/claims/{claim.id}/approve/").status_code, 403)
        self.unclaimed.refresh_from_db()
        self.assertIsNone(self.unclaimed.owner)

    def test_staff_approval_assigns_owner_and_closes_other_claims(self):
        self.claim(self.unclaimed, self.claimer)
        self.claim(self.unclaimed, self.claimer2)
        first = ClaimRequest.objects.get(claimant=self.claimer)

        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(f"{API}/claims/").data["count"], 2)
        response = self.client.post(f"{API}/claims/{first.id}/approve/", {"note": "Checked"},
                                    format="json")
        self.assertEqual(response.status_code, 200)

        self.unclaimed.refresh_from_db()
        self.assertEqual(self.unclaimed.owner, self.claimer)
        self.assertEqual(self.unclaimed.status, Business.Status.CLAIMED)
        first.refresh_from_db()
        self.assertEqual(first.state, ClaimRequest.State.APPROVED)
        self.assertEqual(first.reviewed_by, self.staff)
        other = ClaimRequest.objects.get(claimant=self.claimer2)
        self.assertEqual(other.state, ClaimRequest.State.REJECTED)

    def test_only_staff_can_modify_categories(self):
        self.client.force_authenticate(self.claimer)
        self.assertEqual(
            self.client.post(
                f"{API}/categories/", {"name": "Spam"}, format="json"
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.delete(f"{API}/categories/{self.category.id}/").status_code,
            403,
        )

        self.client.force_authenticate(self.staff)
        self.assertEqual(
            self.client.post(
                f"{API}/categories/", {"name": "Legit"}, format="json"
            ).status_code,
            201,
        )

        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(f"{API}/categories/").status_code, 200)

    def test_claim_cannot_be_reviewed_twice(self):
        self.claim(self.unclaimed, self.claimer)
        claim = ClaimRequest.objects.get()
        self.client.force_authenticate(self.staff)
        self.client.post(f"{API}/claims/{claim.id}/approve/")
        self.assertEqual(self.client.post(f"{API}/claims/{claim.id}/reject/").status_code, 409)

    def test_rejection_leaves_listing_unclaimed(self):
        self.claim(self.unclaimed, self.claimer)
        claim = ClaimRequest.objects.get()
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post(f"{API}/claims/{claim.id}/reject/").status_code, 200)
        self.unclaimed.refresh_from_db()
        self.assertIsNone(self.unclaimed.owner)
        self.assertEqual(self.unclaimed.status, Business.Status.UNCLAIMED)

    # ---- privilege escalation ----
    def test_owner_cannot_self_verify_or_change_status(self):
        self.client.force_authenticate(self.owner)
        self.client.patch(f"{API}/businesses/{self.claimed.id}/",
                          {"is_verified": True, "status": "unclaimed"}, format="json")
        self.claimed.refresh_from_db()
        self.assertFalse(self.claimed.is_verified)
        self.assertEqual(self.claimed.status, Business.Status.CLAIMED)

    def test_non_staff_cannot_edit_ownerless_listing(self):
        self.client.force_authenticate(self.claimer)
        response = self.client.patch(f"{API}/businesses/{self.unclaimed.id}/",
                                     {"name": "Hijacked"}, format="json")
        self.assertIn(response.status_code, (403, 404))
        self.unclaimed.refresh_from_db()
        self.assertEqual(self.unclaimed.name, "Unclaimed Shop")

    def test_api_created_listing_is_claimed_and_not_claimable(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(f"{API}/businesses/", {
            "name": "Fresh Shop", "address": "9 New St", "contact_info": "0711111111",
            "services": "testing", "category_id": self.category.id,
        }, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        created = Business.objects.get(name="Fresh Shop")
        self.assertEqual(created.owner, self.owner)
        self.assertEqual(created.status, Business.Status.CLAIMED)
        self.assertEqual(self.claim(created, self.claimer).status_code, 409)

    # ---- my claims ----
    def test_my_claims_only_shows_own_claims(self):
        self.claim(self.unclaimed, self.claimer)
        self.client.force_authenticate(self.claimer2)
        self.assertEqual(self.client.get(f"{API}/my-claims/").data["count"], 0)
        self.client.force_authenticate(self.claimer)
        self.assertEqual(self.client.get(f"{API}/my-claims/").data["count"], 1)
        self.client.force_authenticate(None)
        self.assertIn(self.client.get(f"{API}/my-claims/").status_code, (401, 403))


class RegistrationTests(APITestCase):
    def setUp(self):
        cache.clear()

    def register(self, **overrides):
        data = {"username": "newuser", "email": "new@example.com",
                "password": "Str0ng-Pass-9731"}
        data.update(overrides)
        return self.client.post("/api/register/", data, format="json")

    def test_register_then_login(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        token = self.client.post("/api/token/", {"username": "newuser",
                                 "password": "Str0ng-Pass-9731"}, format="json")
        self.assertEqual(token.status_code, 200)
        self.assertIn("access", token.data)

    def test_weak_password_rejected(self):
        self.assertEqual(self.register(password="12345678").status_code, 400)

    def test_duplicate_email_rejected(self):
        self.register()
        self.assertEqual(self.register(username="other").status_code, 400)

    def test_cannot_self_register_as_staff(self):
        self.register(is_staff=True, is_superuser=True)
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)