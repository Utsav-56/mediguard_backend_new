from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import UserProfile


class DobIsoFormatTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/auth/register/"  # path from main urls
        self.me_url = "/auth/me/"
        self.user_model = get_user_model()

    def test_signup_accepts_and_returns_iso_dob(self):
        payload = {
            "email": "iso.test@example.com",
            "password": "StrongPass123!",
            "first_name": "Iso",
            "last_name": "Test",
            "age": 30,
            "gender": "male",
            "dob": "1990-05-01",
        }

        resp = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", resp.data)
        self.assertIn("dob", resp.data["user"])
        self.assertEqual(resp.data["user"]["dob"], "1990-05-01")

    def test_profile_patch_updates_dob_and_returns_iso(self):
        # Create a user directly
        user = self.user_model.objects.create_user(
            email="patch.test@example.com", password="StrongPass123!"
        )
        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            first_name="Patch",
            last_name="User",
            age=25,
            gender="female",
            dob="1995-01-01",
        )

        # Authenticate
        self.client.force_authenticate(user=user)

        resp = self.client.patch(self.me_url, {"dob": "1992-02-02"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("user", resp.data)
        self.assertEqual(resp.data["user"]["dob"], "1992-02-02")
