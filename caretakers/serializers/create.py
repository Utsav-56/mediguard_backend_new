import re
from caretakers.models import CareGivers
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class CaregiverCreateSerializer(ModelSerializer):
    class Meta:
        model = CareGivers
        fields = [
            "id",
            "user",
            "caregiver",
            "contact_number",
            "email",
            "nick_name",
            "whatsapp_number",
            "address",
        ]
        read_only_fields = ["id", "user"]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs

        caregiver = attrs.get("caregiver")
        if caregiver == request.user:
            raise serializers.ValidationError("User cannot be their own caregiver.")

        if CareGivers.objects.filter(user=request.user, caregiver=caregiver).exists():
            raise serializers.ValidationError(
                "This caregiver is already added for the user."
            )

        return attrs

    def validate_contact_number(self, value):
        """Validate contact number format"""
        if not value:
            return value
        digits = re.sub(r"\D", "", value)
        if len(digits) < 7 or len(digits) > 15:
            raise serializers.ValidationError("Invalid contact number.")
        return value
