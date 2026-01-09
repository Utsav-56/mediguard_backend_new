import os

from rest_framework import serializers
from accounts.models import User
from accounts.serializers import base_name_validator
from django.contrib.auth.password_validation import validate_password


class ProfilePictureUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("profile_pic",)

    def validate_profile_pic(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image must be under 5MB.")

        if not value.content_type.startswith("image/"):
            raise serializers.ValidationError("Only image files are allowed.")

        return value

    def update(self, instance, validated_data):
        if instance.profile_pic and "profile_pic" in validated_data:
            if os.path.isfile(instance.profile_pic.path):
                os.remove(instance.profile_pic.path)

        return super().update(instance, validated_data)


class PasswordUpdateSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_current_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        # Add password strength validation if needed

        try:
            validate_password(value, user=self.instance)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.messages)

        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class FirstNameUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name",)

    def validate_first_name(self, value):
        return base_name_validator(value, "First name")
