from rest_framework import serializers
from accounts.models import User
from caretakers.models import CareGivers


class UserMiniSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]

    def get_first_name(self, obj):
        try:
            return obj.profile.first_name
        except Exception:
            return ""

    def get_last_name(self, obj):
        try:
            return obj.profile.last_name
        except Exception:
            return ""


class CaregiverDetailSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)  # the person who will be cared for
    caregiver = UserMiniSerializer(read_only=True)  # the person providing care

    class Meta:
        model = CareGivers
        fields = [
            "id",
            "user",
            "caregiver",
            "contact_number",
            "email",
            "nick_name",
            "address",
            "added_at",
            "updated_at",
        ]


class CaregiverBasicGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareGivers
        fields = ["id", "contact_number", "email", "nick_name", "address"]


class CaretakerBasicGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareGivers
        fields = ["id", "contact_number", "email", "nick_name", "address"]
