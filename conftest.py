"""
Global pytest fixtures for the project.

- Provides a DRF APIClient for easy testing of API endpoints.
- Resolves account endpoints via named routes with safe URL fallbacks.
- Creates a valid password and user payloads for registration.
- Safely creates a sample image file for upload tests, using a real picture if present on the machine, otherwise generating a dummy image.
- Overrides MEDIA_ROOT to a temporary directory during tests to avoid polluting local storage.
"""

import io
import os
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient

# Optional Pillow import for generating an image; fallback if not installed.
try:
    from PIL import Image

    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def _resolve_url(name: str, default: str) -> str:
    """
    Try resolving a URL by name, falling back to a sensible default path.

    This keeps tests resilient if route names differ slightly.
    """
    try:
        return reverse(name)
    except NoReverseMatch:
        return default
    except Exception:
        return default


@pytest.fixture(scope="session")
def register_url():
    """
    Registration endpoint URL.

    Attempts to resolve 'accounts:register' first; falls back to '/accounts/register/'.
    """
    return _resolve_url("accounts:register", "/accounts/register/")


@pytest.fixture(scope="session")
def login_url():
    """
    Login endpoint URL.

    Attempts to resolve 'accounts:login' first; falls back to '/accounts/login/'.
    """
    return _resolve_url("accounts:login", "/accounts/login/")


@pytest.fixture
def api_client():
    """
    DRF APIClient instance for making HTTP requests in tests.
    """
    return APIClient()


@pytest.fixture(scope="session")
def valid_password():
    """
    A password designed to satisfy strong password validators.
    """
    return "S3cure!Passw0rd123"


@pytest.fixture
def sample_image_file(tmp_path):
    """
    Returns a SimpleUploadedFile suitable for multipart upload tests.

    If a local image exists at the user-provided path, it uses that; otherwise,
    it generates a small in-memory JPEG or binary blob as a fallback.
    """
    local_img_path = (
        r"C:\Users\HELIOS\Pictures\Wallpapers\qh4vNT0-dark-sky-wallpaper.jpg"
    )
    filename = "profile.jpg"

    if os.path.exists(local_img_path):
        with open(local_img_path, "rb") as f:
            content = f.read()
        return SimpleUploadedFile(filename, content, content_type="image/jpeg")

    # Generate a small image if Pillow is available; else use a tiny binary blob.
    if PIL_AVAILABLE:
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (64, 64), color=(10, 10, 10))
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)
        return SimpleUploadedFile(filename, img_bytes.read(), content_type="image/jpeg")
    else:
        return SimpleUploadedFile(
            filename, b"\xff\xd8\xff\xe0" + b"\x00" * 128, content_type="image/jpeg"
        )


@pytest.fixture(autouse=True)
def temp_media_root(tmp_path, settings):
    """
    Automatically sets MEDIA_ROOT to a temporary directory during tests.

    Prevents test uploads from polluting local development media storage.
    """
    settings.MEDIA_ROOT = tmp_path / "test_media"
    settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    return settings.MEDIA_ROOT


@pytest.fixture
def registration_payload(valid_password, sample_image_file):
    """
    Returns a baseline user registration payload.

    Note: Adjust field names to match your serializer if they differ.
    """
    return {
        "email": "test.user@example.com",
        "password": valid_password,
        # Common optional fields (adjust to your schema as needed):
        "first_name": "Test",
        "last_name": "User",
        "profile_picture": sample_image_file,  # multipart upload
        "health_info": {
            "blood_group": "O+",
            "allergies": ["pollen", "dust"],
            "conditions": ["hypertension"],
        },
    }


@pytest.fixture
def minimal_registration_payload(valid_password):
    """
    Returns a minimal payload expected to pass validation in many setups.
    """
    return {
        "email": "minimal.user@example.com",
        "password": valid_password,
    }


@pytest.fixture
def existing_user(valid_password, db):
    """
    Creates and returns an active user in the database.

    Uses get_user_model() for maximum compatibility with custom User models.
    """
    User = get_user_model()
    email = "existing.user@example.com"
    try:
        user = User.objects.create_user(email=email, password=valid_password)
    except TypeError:
        # Fallback path if create_user signature differs; manually set password.
        user = User(email=email, is_active=True)
        user.set_password(valid_password)
        user.save()
    return user


@pytest.fixture
def inactive_user(valid_password, db):
    """
    Creates and returns an inactive user for login tests.
    """
    User = get_user_model()
    email = "inactive.user@example.com"
    try:
        user = User.objects.create_user(
            email=email, password=valid_password, is_active=False
        )
    except TypeError:
        user = User(email=email, is_active=False)
        user.set_password(valid_password)
        user.save()
    return user
