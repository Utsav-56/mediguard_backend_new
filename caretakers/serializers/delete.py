from rest_framework.serializers import ModelSerializer
from caretakers.models import CareGivers


class CaregiverRemoveSerializer(ModelSerializer):
    class Meta:
        model = CareGivers
        fields = ["id", "user", "caregiver"]

        read_only_fields = ["id"]
