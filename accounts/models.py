import os.path

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

from accounts.managers import CustomUserManager


def profile_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    # instance here will be UserProfile
    filename = f"user_{instance.user.id}_profile.{ext}"
    return os.path.join("profile_pics", filename)


class User(AbstractBaseUser, PermissionsMixin):
    # Auth related info ONLY
    email = models.EmailField(unique=True, db_index=True, null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def username(self):
        return self.email

    def __str__(self):
        return self.email

    def get_user_info(self):
        """
        Helper method to get full user info including profile.
        """
        try:
            profile = self.profile
            return {
                "id": self.id,
                "email": self.email,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "full_name": profile.full_name,
                "age": profile.age,
                "gender": profile.gender,
                "dob": profile.dob,
                "profile_pic": profile.profile_pic.url if profile.profile_pic else None,
                "blood_group": profile.blood_group,
                "weight": profile.weight,
                "height": profile.height,
                "allergies": profile.allergies,
                "chronic_conditions": profile.chronic_conditions,
                "medications": profile.medications,
                "emergency_contact_name": profile.emergency_contact_name,
                "emergency_contact_number": profile.emergency_contact_number,
                "emergency_contact_relation": profile.emergency_contact_relation,
                "family_medical_history": profile.family_medical_history,
                "insurance_provider": profile.insurance_provider,
                "insurance_policy_number": profile.insurance_policy_number,
                "address": profile.address,
                "phone_number": profile.phone_number,
                "contact_email": profile.contact_email,
            }
        except Exception:
            # Fallback if profile doesn't exist yet
            return {
                "id": self.id,
                "email": self.email,
                "first_name": "",
                "last_name": "",
                "full_name": "",
            }


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    # Mandatory fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()

    # Optional fields
    profile_pic = models.ImageField(
        upload_to=profile_image_upload_path, blank=True, null=True
    )
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)  # in kg
    height = models.FloatField(blank=True, null=True)  # in cm

    # Medical history / Info
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relation = models.CharField(max_length=100, blank=True, null=True)

    # Family Medical History
    family_medical_history = models.TextField(blank=True, null=True)

    # Insurance Info
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)

    # Other fields
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"Profile of {self.user.email}"
