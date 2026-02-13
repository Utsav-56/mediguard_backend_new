from django.db import models

import os.path

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

import uuid


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

    @property
    def caregivers(self):
        """Get all users who are caregivers for this user (users who care for self)."""
        # Users who are caregivers for this user:
        # CareGivers model has caregiver -> User FK with related_name "cared_for_users".
        return User.objects.filter(cared_for_users__user=self)

    @property
    def cared_for_users(self):
        """Get all users for whom this user is a caregiver."""
        # Users for whom self is a caregiver:
        # CareGivers.model has user -> User FK with related_name "caretakers".
        return User.objects.filter(caretakers__caregiver=self)

    @property
    def is_caretaker(self):
        """Check if this user is a caretaker for any other user"""
        return self.cared_for_users.exists()

    @property
    def full_info(self):
        """Get complete user info including profile and health info"""
        from accounts.details.details_serializers import CompleteUserGetSerializer

        return CompleteUserGetSerializer(self).data


class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Mandatory fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()

    # Sync Metadata
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    # Optional fields
    profile_pic = models.ImageField(
        upload_to=profile_image_upload_path, blank=True, null=True
    )

    # Family Medical History
    family_medical_history = models.TextField(blank=True, null=True)

    # Insurance Info
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)

    # Other fields
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(
        blank=True, null=True
    )  # this is different from auth email
    emergency_contact_email = models.EmailField(
        blank=True, null=True, help_text="Email of the emergency contact/caretaker"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"Profile of {self.user.email}"


# user profile health info for basic qsns like bloof prressure,  allergies, sugar levels etc.
# they are just one question per user so there is a one to one relationship
class HealthInfo(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="health_info"
    )

    blood_group = models.CharField(max_length=10, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)  # in kg
    height = models.FloatField(blank=True, null=True)  # in cm

    # Medical history / Info
    allergies = models.TextField(blank=True, null=True)
    chronic_conditions = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)

    record_date = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Health Info for {self.user.email} on {self.record_date}"


"""
Example response of getting user info in single dict format:
{
    id,
    email,
    // no password is sent back
    
    is_caretaker: true/false,  // whether the user is a caretaker for any other user

    caregivers: [ // if someone is a caregiver for this user
        ..... all list of caregivers with their info ..... including the updated and created timestamps
    ],

    ....

    "caretakers" :[ // those for whom this user is a caregiver
        ..... all list of caretakers with their info ..... including the updated and created timestamps
    ],

    "health_info": {
        ..... all health info fields .....
    },

    .... others models if leftout








}




"""
