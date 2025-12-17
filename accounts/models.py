from django.db import models

# Create your models here.
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.db import models


def user_profile_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/profile_images/user_<id>/<filename>
    ext = filename.split(".")[-1]
    return f"profile_images/user_{instance.id}.{ext}"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            # 1. Check length min of 7 and max of 13 digits (excluding +)
            RegexValidator(
                regex=r"^\+?\d{7,13}$",
                message="Phone number must be between 7-13 digits",
            ),
            # 2. Check if it contains anything other than + and digits
            RegexValidator(
                regex=r"^[+\d]+$",
                message="Phone number can only contain digits or a plus sign.",
            ),
            RegexValidator(
                regex=r"^\+?\d+$",
                message="Phone number must not contain consecutive special characters.",
            ),
        ],
    )
    address = models.TextField(blank=True, null=True)

    profile_image = models.ImageField(
        upload_to=user_profile_image_path, blank=True, null=True
    )  # ✅ Added

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def save(self, *args, **kwargs):
        # first save to generate ID
        if not self.id:
            saved_image = self.profile_image
            self.profile_image = None
            super().save(*args, **kwargs)
            self.profile_image = saved_image

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(" ")

    def get_profile_image_url(self):
        if self.profile_image:
            request = getattr(self, "_request", None)
            if request:
                return request.build_absolute_uri(self.profile_image.url)
            else:
                # Fallback to manual construction
                return f"{settings.MEDIA_URL}{self.profile_image.name}"
        return None

    def get_user_info(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "address": self.address,
            "profile_image": self.get_profile_image_url(),
        }

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


