from django.test import TestCase

# Create your tests here.
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