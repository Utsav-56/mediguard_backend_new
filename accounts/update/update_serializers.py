from accounts.models import UserProfile, HealthInfo
from rest_framework.serializers import Serializer
from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password


class UserUpdateSerializer(Serializer):
    """
    Updates user profile + health info
    No auth fields
    No timestamps
    No UUIDs
    """

    # Profile fields
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    age = serializers.IntegerField(required=False)
    gender = serializers.ChoiceField(
        choices=["male", "female", "other"], required=False
    )
    dob = serializers.DateField(required=False)

    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    family_medical_history = serializers.CharField(required=False, allow_blank=True)

    insurance_provider = serializers.CharField(required=False, allow_blank=True)
    insurance_policy_number = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_email = serializers.EmailField(required=False, allow_null=True)

    profile_pic = serializers.ImageField(required=False, allow_null=True)

    # Health info
    blood_group = serializers.CharField(required=False, allow_blank=True)
    weight = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    allergies = serializers.CharField(required=False, allow_blank=True)
    chronic_conditions = serializers.CharField(required=False, allow_blank=True)
    medications = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        user = instance

        # Profile updates
        # We handle get_or_create safely by providing defaults if we have to create
        defaults = {
            "first_name": validated_data.get("first_name", "User"),
            "last_name": validated_data.get("last_name", ""),
            "age": validated_data.get("age", 0),
            "gender": validated_data.get("gender", "other"),
            "dob": validated_data.get("dob", "2000-01-01"),
        }
        profile, created = UserProfile.objects.get_or_create(user=user, defaults=defaults)

        # Update fields if provided
        profile_fields = [
            "first_name",
            "last_name",
            "age",
            "gender",
            "dob",
            "phone_number",
            "address",
            "contact_email",
            "family_medical_history",
            "insurance_provider",
            "insurance_policy_number",
            "emergency_contact_email",
        ]
        
        for field in profile_fields:
            if field in validated_data:
                setattr(profile, field, validated_data[field])

        if "profile_pic" in validated_data:
            profile.profile_pic = validated_data["profile_pic"]

        profile.save()

        # Health info updates
        health, _ = HealthInfo.objects.get_or_create(user=user)
        health_fields = [
            "blood_group",
            "weight",
            "height",
            "allergies",
            "chronic_conditions",
            "medications",
        ]
        
        for field in health_fields:
            if field in validated_data:
                setattr(health, field, validated_data[field])

        health.save()

        return user


class PasswordUpdateSerializer(Serializer):
    """
    Serializer for updating user password.

    Validates old password and enforces new password requirements.
    Must be used with proper authentication context.
    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Your current password for verification.",
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        help_text="Your new password (must meet security requirements).",
    )

    def validate_old_password(self, value):
        """
        Validate that old password is provided and not empty.

        Args:
            value: The old password value from request data

        Returns:
            The validated old password value

        Raises:
            ValidationError: If password is empty
        """
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Old password is required to set a new password."
            )
        return value

    def validate_new_password(self, value):
        """
        Validate new password using Django's built-in password validators.

        Args:
            value: The new password value from request data

        Returns:
            The validated new password value

        Raises:
            ValidationError: If password is empty or fails validation
        """
        if not value or not value.strip():
            raise serializers.ValidationError("New password cannot be empty.")

        # Django's validate_password raises ValidationError if invalid
        # It checks: minimum length, common patterns, numeric-only, etc.
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(
                f"New password does not meet security requirements: {', '.join(e.messages)}"
            )

        return value

    def validate(self, attrs):
        """
        Verify that old password matches the user's current password.

        Args:
            attrs: Dictionary of all field values

        Returns:
            The validated attributes dictionary

        Raises:
            ValidationError: If old password is incorrect
        """
        # Get user from request context
        user = self.context.get("request").user

        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")

        # Ensure both passwords exist before proceeding
        if not old_password or not new_password:
            raise serializers.ValidationError(
                "Both old and new passwords are required."
            )

        # Verify the old password is correct
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {
                    "old_password": "The old password you provided is incorrect. "
                    "Please try again."
                }
            )

        # Prevent using the same password
        if old_password == new_password:
            raise serializers.ValidationError(
                {
                    "new_password": "New password cannot be the same as your old password. "
                    "Please choose a different password."
                }
            )

        return attrs

    def save(self, **kwargs):
        """
        Save the new password to the user account.

        Returns:
            The updated User instance
        """
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user
