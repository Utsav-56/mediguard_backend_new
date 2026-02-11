from caretakers.models import CareGivers
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
import re


class CaregiverUpdateSerializer(ModelSerializer):
    class Meta:
        model = CareGivers
        fields = [
            "id",
            "user",
            "caregiver",
            "contact_number",
            "whatsapp_number",
            "email",
            "nick_name",
            "address",
            "added_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "caregiver", "added_at", "updated_at"]

    def validate_contact_number(self, value):
        """Validate contact number format"""
        if not value:
            return value
        digits = re.sub(r"\D", "", value)
        if len(digits) < 7 or len(digits) > 15:
            raise serializers.ValidationError("Invalid contact number.")
        return value
