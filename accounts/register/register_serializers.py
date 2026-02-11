from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from accounts.models import User, UserProfile, HealthInfo
from caretakers.models import CareGivers


class UserSignupSerializer(UserCreateSerializer):
    """Extended user creation serializer with profile and health info"""

    # UserProfile fields
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=["male", "female", "other"])
    dob = serializers.DateField()

    # HealthInfo fields (optional)
    blood_group = serializers.CharField(max_length=10, required=False, allow_blank=True)
    weight = serializers.FloatField(required=False)
    height = serializers.FloatField(required=False)
    allergies = serializers.CharField(required=False, allow_blank=True)
    chronic_conditions = serializers.CharField(required=False, allow_blank=True)
    medications = serializers.CharField(required=False, allow_blank=True)

    # UserProfile optional fields
    phone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    address = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    family_medical_history = serializers.CharField(required=False, allow_blank=True)
    insurance_provider = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    insurance_policy_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )

    profile_pic = serializers.ImageField(
        required=False, allow_null=True, allow_empty_file=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "age",
            "gender",
            "dob",
            "blood_group",
            "weight",
            "height",
            "allergies",
            "chronic_conditions",
            "medications",
            "phone_number",
            "address",
            "contact_email",
            "family_medical_history",
            "insurance_provider",
            "insurance_policy_number",
            # first create the user and other  info and give profile pic later
            "profile_pic",
        ]

        extra_kwargs = {"password": {"write_only": True}, "terms": {"write_only": True}}

    def validate(self, attrs):
        """Override to remove profile fields from main user validation"""

        self.profile_data = {
            "first_name": attrs.pop("first_name"),
            "last_name": attrs.pop("last_name"),
            "age": attrs.pop("age"),
            "gender": attrs.pop("gender"),
            "dob": attrs.pop("dob"),
            "phone_number": attrs.pop("phone_number", ""),
            "address": attrs.pop("address", ""),
            "contact_email": attrs.pop("contact_email", ""),
            "family_medical_history": attrs.pop("family_medical_history", ""),
            "insurance_provider": attrs.pop("insurance_provider", ""),
            "insurance_policy_number": attrs.pop("insurance_policy_number", ""),
        }

        self.health_data = {
            "blood_group": attrs.pop("blood_group", ""),
            "weight": attrs.pop("weight", None),
            "height": attrs.pop("height", None),
            "allergies": attrs.pop("allergies", ""),
            "chronic_conditions": attrs.pop("chronic_conditions", ""),
            "medications": attrs.pop("medications", ""),
        }

        # main user model data
        self.main_user_data = {
            "email": attrs.get("email"),
            "password": attrs.get("password"),
        }

        self.profile_pic = attrs.pop("profile_pic", None)
        return super().validate(attrs)

    def create(self, validated_data):
        """Create user with profile and health info in a single transaction"""

        print(f"Validated data in create: {validated_data}")

        # Create user using parent class
        user = super().create(validated_data)

        # Create profile and health info
        UserProfile.objects.create(user=user, **self.profile_data)
        HealthInfo.objects.create(user=user, **self.health_data)
        # if profile_pic is provided, set it
        profile_pic = validated_data.get("profile_pic", None)
        if profile_pic:
            user.profile.profile_pic = self.profile_pic
            user.profile.save()

        return user
