from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import rest_framework.serializers as serializers


class UserLoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for user login
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        """Check if user with this email exists"""
        from accounts.models import User

        self.user = User.objects.filter(email=value).first()
        if not self.user or self.user is None:
            raise serializers.ValidationError("User with this email does not exist.")

        return value

    def validate(self, attrs):
        data = super().validate(attrs)

        print(f"Serializer validated data: {data}")

        data["user"] = self.user.full_info  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue] # ty:ignore[possibly-missing-attribute]
        return data
