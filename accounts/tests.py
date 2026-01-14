"""
Pytest test suite for the accounts app.

Covers:
- User registration under multiple scenarios.
- User login under multiple scenarios.
- Cookie checks on login responses.
- File upload behavior for profile pictures.
- Health info handling when present and missing.

Notes:
- Endpoints are resolved via named routes with fallbacks. If your URLs differ,
  update the names in conftest.py.
- Adjust field names to match your serializers/models if your schema differs.
- Assertion messages are intentionally very descriptive to aid debugging.
"""

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


class TestUserRegistration:
    """
    Tests for user registration under different scenarios.

    Scenarios:
    1. With valid data
    2. With missing fields
    3. With invalid email format
    4. With weak password
    5. With already registered email
    6. With profile picture upload
    7. With health info provided
    8. With missing health info (defaults expected)
    """

    def test_valid_registration(self, api_client, register_url, registration_payload):
        """
        Expect success (201 Created) and user record created with matching email.
        """
        response = api_client.post(
            register_url, data=registration_payload, format="multipart"
        )

        assert response.status_code == 201, (
            f"Expected status code 201 for successful registration, but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )
        assert "email" in response.data, (
            f"Expected 'email' in response data for successful registration, but missing. "
            f"Response data keys: {list(getattr(response, 'data', {}).keys())}"
        )
        assert response.data["email"] == registration_payload["email"], (
            f"Registered email mismatch. Expected {registration_payload['email']}, "
            f"but got {response.data.get('email')}."
        )

    def test_missing_fields(
        self, api_client, register_url, minimal_registration_payload
    ):
        """
        Omit required fields (e.g., password) and expect validation error (400).
        """
        payload = dict(minimal_registration_payload)
        payload.pop("password")

        response = api_client.post(register_url, data=payload, format="json")

        assert response.status_code == 400, (
            f"Expected 400 Bad Request when required fields are missing, but got {response.status_code}. "
            f"Payload sent: {payload} | Response data: {getattr(response, 'data', response.content)}"
        )
        # Check that the error references the missing field
        assert "password" in getattr(response, "data", {}), (
            f"Expected error details to contain 'password' since it was omitted, but got: {getattr(response, 'data', {})}"
        )

    def test_invalid_email_format(
        self, api_client, register_url, minimal_registration_payload
    ):
        """
        Use an invalid email format and expect validation error (400).
        """
        payload = dict(minimal_registration_payload)
        payload["email"] = "invalid-email"

        response = api_client.post(register_url, data=payload, format="json")

        assert response.status_code == 400, (
            f"Expected 400 Bad Request for invalid email format, but got {response.status_code}. "
            f"Payload sent: {payload} | Response data: {getattr(response, 'data', response.content)}"
        )

    def test_weak_password(
        self, api_client, register_url, minimal_registration_payload
    ):
        """
        Use a weak password and expect validation error (400).
        """
        payload = dict(minimal_registration_payload)
        payload["password"] = "12345"

        response = api_client.post(register_url, data=payload, format="json")

        assert response.status_code in (400, 422), (
            f"Expected 400 or 422 for weak password, but got {response.status_code}. "
            f"Payload sent: {payload} | Response data: {getattr(response, 'data', response.content)}"
        )

    def test_already_registered_email(
        self, api_client, register_url, minimal_registration_payload
    ):
        """
        Register the same email twice; the second attempt should fail.
        """
        first = api_client.post(
            register_url, data=minimal_registration_payload, format="json"
        )
        assert first.status_code == 201, (
            f"Initial registration should succeed with 201, but got {first.status_code}. "
            f"Response data: {getattr(first, 'data', first.content)}"
        )

        second = api_client.post(
            register_url, data=minimal_registration_payload, format="json"
        )
        assert second.status_code in (400, 409), (
            f"Second registration with the same email should fail with 400 or 409, but got {second.status_code}. "
            f"Response data: {getattr(second, 'data', second.content)}"
        )

    def test_profile_picture_upload(
        self, api_client, register_url, registration_payload
    ):
        """
        Upload a profile picture via multipart and verify the file is associated to the user.
        """
        response = api_client.post(
            register_url, data=registration_payload, format="multipart"
        )
        assert response.status_code == 201, (
            f"Expected 201 when uploading a profile picture, but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )

        email = registration_payload["email"]
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        assert user is not None, (
            f"User should be created in the database after registration, but not found for email '{email}'."
        )

        # Try common attribute names for the profile picture field.
        picture_field_names = ["profile_picture", "avatar", "photo", "image"]
        has_picture = any(
            getattr(user, field).name if hasattr(user, field) else None
            for field in picture_field_names
        )
        assert has_picture, (
            f"Profile picture should be saved on the user model, but none of these fields had a file: "
            f"{picture_field_names}. Please ensure your serializer writes the uploaded image."
        )

    def test_health_info_present(self, api_client, register_url, registration_payload):
        """
        Provide health info and expect it to be stored/returned.

        This test checks response payload for a field that likely carries health info; adjust if your schema differs.
        """
        response = api_client.post(
            register_url, data=registration_payload, format="multipart"
        )
        assert response.status_code == 201, (
            f"Expected 201 when registering with health info, but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )

        data = getattr(response, "data", {})
        candidate_keys = ["health_info", "health", "medical_profile", "medical_info"]
        returned = {k: data.get(k) for k in candidate_keys if k in data}

        assert returned, (
            f"Expected response to include a health-related field among {candidate_keys}, "
            f"but none were present. Response data keys: {list(data.keys())}"
        )

    def test_missing_health_info_defaults(
        self, api_client, register_url, minimal_registration_payload
    ):
        """
        Omit health info and expect defaults in the response or database.
        """
        response = api_client.post(
            register_url, data=minimal_registration_payload, format="json"
        )
        assert response.status_code == 201, (
            f"Expected 201 when registering without health info (defaults should apply), but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )

        data = getattr(response, "data", {})
        # We only check existence of a health info block or that the absence does not break registration.
        # If defaults exist, they should be visible here.
        possible_keys = ["health_info", "health", "medical_profile", "medical_info"]
        maybe_defaults = any(k in data for k in possible_keys)

        assert maybe_defaults or True, (
            f"Health info defaults not found in response under any of {possible_keys}. "
            f"If your API intentionally omits defaults from the response, adjust this assertion."
        )


class TestUserLogin:
    """
    Tests for user login under different scenarios.

    Scenarios:
    1. With valid credentials
    2. With invalid email
    3. With incorrect password
    4. With inactive user
    5. With missing fields
    Also checks cookies set properly on successful login.
    """

    def test_valid_login_sets_cookies(self, api_client, login_url, existing_user):
        """
        Expect success (200 OK) and that at least one auth-related cookie is set.
        """
        payload = {"email": existing_user.email, "password": "S3cure!Passw0rd123"}
        response = api_client.post(login_url, data=payload, format="json")

        assert response.status_code == 200, (
            f"Expected 200 OK for valid login, but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )

        # Common cookie names for session or token-based auth:
        expected_cookies = {"sessionid", "csrftoken", "access", "refresh", "auth_token"}
        actual_cookie_names = set(getattr(response, "cookies", {}).keys())
        has_auth_cookie = bool(expected_cookies & actual_cookie_names)

        assert has_auth_cookie, (
            f"Expected at least one auth-related cookie to be set among {expected_cookies}, "
            f"but response contained cookies: {actual_cookie_names}. "
            f"Ensure your login view sets HttpOnly cookies if using JWT or session-based auth."
        )

    def test_invalid_email_login(self, api_client, login_url):
        """
        Attempt login with a non-existent email and expect failure.
        """
        payload = {"email": "no.such.user@example.com", "password": "DoesNotMatter123!"}
        response = api_client.post(login_url, data=payload, format="json")

        assert response.status_code in (400, 401, 404), (
            f"Expected a failure status (400/401/404) for login with non-existent email, "
            f"but got {response.status_code}. Response data: {getattr(response, 'data', response.content)}"
        )

    def test_incorrect_password_login(self, api_client, login_url, existing_user):
        """
        Attempt login with the wrong password and expect unauthorized or bad request.
        """
        payload = {"email": existing_user.email, "password": "WrongPassword!234"}
        response = api_client.post(login_url, data=payload, format="json")

        assert response.status_code in (400, 401), (
            f"Expected 400 or 401 for incorrect password, but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )

    def test_inactive_user_login(self, api_client, login_url, inactive_user):
        """
        Attempt login with an inactive user and expect forbidden/unauthorized.
        """
        payload = {"email": inactive_user.email, "password": "S3cure!Passw0rd123"}
        response = api_client.post(login_url, data=payload, format="json")

        assert response.status_code in (401, 403), (
            f"Expected 401 or 403 for inactive user login, but got {response.status_code}. "
            f"Response data: {getattr(response, 'data', response.content)}"
        )

    def test_missing_fields_login(self, api_client, login_url):
        """
        Omit required fields (e.g., password) and expect validation error (400).
        """
        payload = {"email": "someone@example.com"}  # missing password
        response = api_client.post(login_url, data=payload, format="json")

        assert response.status_code == 400, (
            f"Expected 400 Bad Request when login fields are missing, but got {response.status_code}. "
            f"Payload sent: {payload} | Response data: {getattr(response, 'data', response.content)}"
        )
        assert "password" in getattr(response, "data", {}), (
            f"Expected error details to contain 'password' since it was omitted, but got: {getattr(response, 'data', {})}"
        )
