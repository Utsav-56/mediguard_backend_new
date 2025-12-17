from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from .models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    full_name = serializers.CharField(required=True)
    profile_image = serializers.ImageField(
        required=False, allow_null=True
    )  # ✅ optional

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
        )
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}


class UserSerializer(BaseUserSerializer):
    profile_image = serializers.SerializerMethodField()  # ✅ return absolute URL

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "address",
            "profile_image",
        )

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None
