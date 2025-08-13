from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from properties.models import Property, Location, Amenity

User = get_user_model()

class PropertyTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="owner@example.com", password="password123", role=User.PROPERTY_OWNER)
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.location = Location.objects.create(name="Lekki Phase 1", city="Lagos", state="Lagos", country="Nigeria")
        self.amenity1 = Amenity.objects.create(name="Swimming Pool")
        self.amenity2 = Amenity.objects.create(name="Gym")
        self.property_data = {
            "title": "Beautiful Apartment",
            "description": "A spacious apartment in Lekki Phase 1.",
            "price": 50000000.00,
            "property_type": "apartment",
            "listing_type": "for_sale",
            "location": self.location.id,
            "address": "123 Main St, Lekki Phase 1",
            "bedrooms": 3,
            "bathrooms": 3,
            "size": 150.00,
            "amenities": [self.amenity1.id, self.amenity2.id]
        }
        self.property_url = reverse("property-list")

    def test_create_property_authenticated(self):
        """Ensure authenticated property owner can create a property."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.property_url, self.property_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 1)
        self.assertEqual(Property.objects.get().title, "Beautiful Apartment")

    def test_create_property_unauthenticated(self):
        """Ensure unauthenticated user cannot create a property."""
        response = self.client.post(self.property_url, self.property_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_properties(self):
        """Ensure anyone can list properties."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.property_url, self.property_data, format="json")
        self.client.force_authenticate(user=None) # Unauthenticate for listing
        response = self.client.get(self.property_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_property(self):
        """Ensure anyone can retrieve a single property."""
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.property_url, self.property_data, format="json")
        property_id = create_response.data["id"]
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("property-detail", args=[property_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Beautiful Apartment")

    def test_update_property_owner(self):
        """Ensure property owner can update their property."""
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.property_url, self.property_data, format="json")
        property_id = create_response.data["id"]
        updated_data = {"title": "Updated Apartment Title"}
        response = self.client.patch(reverse("property-detail", args=[property_id]), updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Property.objects.get(id=property_id).title, "Updated Apartment Title")

    def test_update_property_other_user(self):
        """Ensure other authenticated users cannot update a property."""
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.property_url, self.property_data, format="json")
        property_id = create_response.data["id"]
        other_user = User.objects.create_user(email="other@example.com", password="password123")
        self.client.force_authenticate(user=other_user)
        updated_data = {"title": "Attempted Update"}
        response = self.client.patch(reverse("property-detail", args=[property_id]), updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_property_owner(self):
        """Ensure property owner can delete their property."""
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.property_url, self.property_data, format="json")
        property_id = create_response.data["id"]
        response = self.client.delete(reverse("property-detail", args=[property_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Property.objects.count(), 0)

    def test_delete_property_admin(self):
        """Ensure admin can delete any property."""
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.property_url, self.property_data, format="json")
        property_id = create_response.data["id"]
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse("property-detail", args=[property_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Property.objects.count(), 0)

    def test_delete_property_other_user(self):
        """Ensure other authenticated users cannot delete a property."""
        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.property_url, self.property_data, format="json")
        property_id = create_response.data["id"]
        other_user = User.objects.create_user(email="other@example.com", password="password123")
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(reverse("property-detail", args=[property_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class PropertyVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(email="owner@example.com", password="password123", role=User.PROPERTY_OWNER)
        self.government_user = User.objects.create_user(email="gov@example.com", password="govpass", role=User.GOVERNMENT)
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.location = Location.objects.create(name="Ikeja", city="Lagos", state="Lagos", country="Nigeria")
        self.property = Property.objects.create(
            title="Unverified House",
            description="Needs verification.",
            price=10000000.00,
            property_type="house",
            listing_type="for_sale",
            location=self.location,
            address="456 Oak Ave",
            owner=self.owner,
            verification_status=Property.PENDING
        )

    def test_government_can_verify_property(self):
        """Ensure government agency can verify a property."""
        self.client.force_authenticate(user=self.government_user)
        response = self.client.patch(reverse("property-detail", args=[self.property.id]), 
                                     {"verification_status": Property.VERIFIED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.verification_status, Property.VERIFIED)
        self.assertEqual(self.property.verified_by, self.government_user)

    def test_admin_can_verify_property(self):
        """Ensure admin can verify a property."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(reverse("property-detail", args=[self.property.id]), 
                                     {"verification_status": Property.VERIFIED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.verification_status, Property.VERIFIED)
        self.assertEqual(self.property.verified_by, self.admin_user)

    def test_non_authorized_cannot_verify_property(self):
        """Ensure non-admin/non-government users cannot verify a property."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(reverse("property-detail", args=[self.property.id]), 
                                     {"verification_status": Property.VERIFIED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.property.refresh_from_db()
        self.assertEqual(self.property.verification_status, Property.PENDING)

    def test_reject_property_with_reason(self):
        """Ensure authorized users can reject a property with a reason."""
        self.client.force_authenticate(user=self.government_user)
        response = self.client.patch(reverse("property-detail", args=[self.property.id]), {
            "verification_status": Property.REJECTED,
            "rejection_reason": "Incomplete documentation"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.property.refresh_from_db()
        self.assertEqual(self.property.verification_status, Property.REJECTED)
        self.assertEqual(self.property.rejection_reason, "Incomplete documentation")

    def test_reject_property_without_reason_fails(self):
        """Ensure rejecting a property without a reason fails."""
        self.client.force_authenticate(user=self.government_user)
        response = self.client.patch(reverse("property-detail", args=[self.property.id]), 
                                     {"verification_status": Property.REJECTED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rejection_reason", response.data)


