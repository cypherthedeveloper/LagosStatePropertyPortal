from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("user-list") # Assuming user-list handles POST for registration
        self.login_url = reverse("token_obtain_pair")
        self.refresh_url = reverse("token_refresh")
        self.user_data = {
            "email": "testuser@example.com",
            "password": "securepassword123",
            "password_confirmation": "securepassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "buyer_renter"
        }
        self.admin_user_data = {
            "email": "admin@example.com",
            "password": "adminpassword123",
            "password_confirmation": "adminpassword123",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }

    def test_user_registration(self):
        """Ensure we can create a new user account."""
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, "testuser@example.com")

    def test_user_login_and_token_obtain(self):
        """Ensure user can log in and obtain JWT tokens."""
        self.client.post(self.register_url, self.user_data, format="json")
        response = self.client.post(self.login_url, {"email": "testuser@example.com", "password": "securepassword123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_refresh(self):
        """Ensure JWT tokens can be refreshed."""
        self.client.post(self.register_url, self.user_data, format="json")
        login_response = self.client.post(self.login_url, {"email": "testuser@example.com", "password": "securepassword123"}, format="json")
        refresh_token = login_response.data["refresh"]
        response = self.client.post(self.refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_admin_user_creation(self):
        """Ensure an admin user can be created."""
        response = self.client.post(self.register_url, self.admin_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(User.objects.get().is_admin)

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="password123", first_name="Test", last_name="User")
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.client.force_authenticate(user=self.user)
        self.profile_url = reverse("user-me")
        self.change_password_url = reverse("user-change-password")

    def test_get_user_profile(self):
        """Ensure authenticated users can retrieve their own profile."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_change_user_password(self):
        """Ensure authenticated users can change their password."""
        response = self.client.post(self.change_password_url, {
            "old_password": "password123",
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepassword"))

    def test_change_password_mismatch(self):
        """Ensure password change fails with mismatching new passwords."""
        response = self.client.post(self.change_password_url, {
            "old_password": "password123",
            "new_password": "newsecurepassword",
            "confirm_password": "mismatch"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_change_password_wrong_old_password(self):
        """Ensure password change fails with incorrect old password."""
        response = self.client.post(self.change_password_url, {
            "old_password": "wrongpassword",
            "new_password": "newsecurepassword",
            "confirm_password": "newsecurepassword"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

class KYCVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", password="password123", role=User.BUYER_RENTER)
        self.admin_user = User.objects.create_superuser(email="admin@example.com", password="adminpass")
        self.government_user = User.objects.create_user(email="gov@example.com", password="govpass", role=User.GOVERNMENT)
        self.kyc_submit_url = reverse("kycverification-submit")
        self.kyc_list_url = reverse("kycverification-list")

    def test_kyc_submission_buyer_renter(self):
        """Ensure buyer/renter can submit KYC with ID details."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.kyc_submit_url, {
            "id_type": "National ID",
            "id_number": "123456789",
            # In a real scenario, id_document would be a File object
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_admin_can_list_kyc_requests(self):
        """Ensure admin can list all KYC verification requests."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.kyc_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_government_can_list_kyc_requests(self):
        """Ensure government agency can list all KYC verification requests."""
        self.client.force_authenticate(user=self.government_user)
        response = self.client.get(self.kyc_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_admin_can_approve_kyc(self):
        """Ensure admin can approve a KYC request."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.kyc_submit_url, {
            "id_type": "National ID",
            "id_number": "123456789",
        }, format="json")
        kyc_obj = self.user.kyc_verification

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(reverse("kycverification-detail", args=[kyc_obj.id]), {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        kyc_obj.refresh_from_db()
        self.assertEqual(kyc_obj.status, "approved")
        self.assertTrue(self.user.is_verified)

    def test_admin_can_reject_kyc_with_reason(self):
        """Ensure admin can reject a KYC request with a reason."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.kyc_submit_url, {
            "id_type": "National ID",
            "id_number": "123456789",
        }, format="json")
        kyc_obj = self.user.kyc_verification

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(reverse("kycverification-detail", args=[kyc_obj.id]), {
            "status": "rejected",
            "rejection_reason": "ID document blurry"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        kyc_obj.refresh_from_db()
        self.assertEqual(kyc_obj.status, "rejected")
        self.assertEqual(kyc_obj.rejection_reason, "ID document blurry")
        self.assertFalse(self.user.is_verified)

    def test_reject_kyc_without_reason_fails(self):
        """Ensure rejecting KYC without a reason fails."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.kyc_submit_url, {
            "id_type": "National ID",
            "id_number": "123456789",
        }, format="json")
        kyc_obj = self.user.kyc_verification

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(reverse("kycverification-detail", args=[kyc_obj.id]), {"status": "rejected"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rejection_reason", response.data)

    def test_unauthorized_kyc_update(self):
        """Ensure non-admin/non-government users cannot update KYC status."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse("kycverification-detail", args=[1]), {"status": "approved"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pending_kyc_list_for_admin(self):
        """Ensure admin can view pending KYC requests."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.kyc_submit_url, {
            "id_type": "Passport",
            "id_number": "987654321",
        }, format="json")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("kycverification-pending"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "pending")

    def test_pending_kyc_list_for_government(self):
        """Ensure government agency can view pending KYC requests."""
        self.client.force_authenticate(user=self.user)
        self.client.post(self.kyc_submit_url, {
            "id_type": "Passport",
            "id_number": "987654321",
        }, format="json")

        self.client.force_authenticate(user=self.government_user)
        response = self.client.get(reverse("kycverification-pending"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "pending")

    def test_pending_kyc_list_unauthorized(self):
        """Ensure non-admin/non-government users cannot view pending KYC requests."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("kycverification-pending"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


