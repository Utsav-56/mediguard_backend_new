from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from .models import User, UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from djoser.serializers import UserSerializer as BaseUserSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user"]

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        if obj.profile_pic and request:
            return request.build_absolute_uri(obj.profile_pic.url)
        return obj.profile_pic.url if obj.profile_pic else None


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Serializer for user registration. Handles both User and UserProfile creation.
    """
    # Mandatory Profile Fields
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    # Accept DOB as epoch timestamp (milliseconds)
    dob = serializers.IntegerField(write_only=True)

    # Optional Profile Fields (can be added here if needed during signup)
    phone_number = serializers.CharField(max_length=20, required=False)
    address = serializers.CharField(required=False)

    class Meta(BaseUserCreateSerializer.Meta):
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
            "phone_number",
            "address",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.password_validation import validate_password
        from django.core import exceptions as django_exceptions
        
        User = get_user_model()
        password = attrs.get("password")
        
        # Filter attrs for User model instantiation to avoid TypeError
        # Only keep fields that are actually on the User model (excluding profile fields like age, gender etc)
        user_field_names = {f.name for f in User._meta.fields}
        user_attrs = {k: v for k, v in attrs.items() if k in user_field_names}
        
        # Create temp user for password validation
        user = User(**user_attrs)
        
        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs

    def validate_email(self, value):
        """Ensure email is unique and valid."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        # Extract profile data
        profile_fields = [
            "first_name", "last_name", "age", "gender", "dob", "phone_number", "address"
        ]
        profile_data = {}
        for field in profile_fields:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)
        
        # Determine DOB from timestamp if it's an integer (epoch ms)
        if 'dob' in profile_data:
            ts = profile_data['dob']
            if isinstance(ts, int):
                from datetime import datetime
                # Assuming milliseconds
                profile_data['dob'] = datetime.fromtimestamp(ts / 1000.0).date()

        # Create user
        user = super().create(validated_data)
        
        # Create profile
        UserProfile.objects.create(user=user, **profile_data)
        
        return user


class UserSerializer(BaseUserSerializer):
    """
    Serializer for user data retrieval. Returns full profile info.
    """
    profile = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "is_active",
            "is_staff",
            "profile",
        ]
        read_only_fields = ["id", "email", "is_active", "is_staff"]

    def get_profile(self, obj):
        return obj.get_user_info()


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["user"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ["user"]
        # Email change is handled by separating User.email and Profile.contact_email
        # but the prompt says "we wont allow to change email". 
        # I'll make sure contact_email can be changed if they want, but User.email (auth) cannot be.
        # Actually I'll just exclude email from here to be safe if that's what they meant.
        # Wait, if they have contact_email in profile, maybe that's what they want to change?
        # "we wont allow to change email" usually refers to the primary email.

    def validate(self, attrs):
        # Additional validation if needed
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context.get("request").user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                "New password cannot be the same as the old password."
            )
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        # password is validated by super().validate(attrs)
        
        User = get_user_model()

        # Check if email exists
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": {"email": f'Provided email "{email}" not found.'}}
            )

        if not user_obj.is_active:
            raise serializers.ValidationError({"detail": "Account is inactive."})

        try:
            data = super().validate(attrs)
        except serializers.ValidationError:
            raise serializers.ValidationError(
                {"detail": {"password": "Password is incorrect for given email."}}
            )

        # Add Custom Data in "user" key as requested
        data["user"] = user_obj.get_user_info()
        
        # Remove tokens from data if we want to ensure they aren't in body
        # However, the view will handle the cookie setting.
        # The user requested: "we will not send the tokens in the response body"
        # So we should probably remove them here or in the view.
        # If we remove them here, the view might fail if it expects them.
        # I'll leave them for now and remove them in the View's post method.

        return data
