from caretakers.serializers.read import CaregiverDetailSerializer
from rest_framework import serializers
from accounts.models import User, UserProfile, HealthInfo
from caretakers.models import CareGivers


class UserGetSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user data"""

    class Meta:
        model = User
        fields = ["id", "email", "is_active", "created_at"]


class HealthInfoGetSerializer(serializers.ModelSerializer):
    """Serializer for HealthInfo model when retrieving user data"""

    class Meta:
        model = HealthInfo
        fields = [
            "blood_group",
            "weight",
            "height",
            "allergies",
            "chronic_conditions",
            "medications",
            "record_date",
            "updated_at",
        ]


class UserProfileGetSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model when retrieving user data"""

    full_name = serializers.CharField(read_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "age",
            "gender",
            "dob",
            "phone_number",
            "address",
            "contact_email",
            "family_medical_history",
            "insurance_provider",
            "insurance_policy_number",
            "updated_at",
            "profile_pic",
        ]

    def get_profile_pic(self, obj):
        """Get full URL for profile picture"""
        request = self.context.get("request")
        if obj.profile_pic and request:
            return request.build_absolute_uri(obj.profile_pic.url)
        return obj.profile_pic.url if obj.profile_pic else None


class CompleteUserGetSerializer(serializers.ModelSerializer):
    """
    Complete serializer for retrieving full user info in single response.
    Returns user data, profile, health info, caregivers, and caretakers.
    """

    profile = UserProfileGetSerializer(read_only=True)
    health_info = HealthInfoGetSerializer(read_only=True)
    caregivers = serializers.SerializerMethodField()
    caretakers = serializers.SerializerMethodField()
    is_caretaker = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "is_active",
            "created_at",
            "profile",
            "health_info",
            "caregivers",
            "caretakers",
            "is_caretaker",
        ]

    def get_caregivers(self, obj):
        """
        Get all users who are caregivers for this user.
        These are emergency contacts who will be notified if user is admitted.
        """
        caretakers = CareGivers.objects.filter(caregiver=obj)
        return CaregiverDetailSerializer(caretakers, many=True).data

    def get_caretakers(self, obj):
        """
        Get all users for whom this user is a caretaker.
        These are users for whom this person gives care in emergencies.
        """
        caretakers = CareGivers.objects.filter(caregiver=obj)
        return CaregiverDetailSerializer(caretakers, many=True).data

    def get_is_caretaker(self, obj):
        """Check if this user is a caretaker for anyone"""
        return CareGivers.objects.filter(caregiver=obj).exists()
