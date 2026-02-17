from rest_framework import generics, permissions

from caretakers.models import CareGivers
from caretakers.serializers.create import CaregiverCreateSerializer
from caretakers.serializers.update import CaregiverUpdateSerializer
from caretakers.serializers.read import CaregiverDetailSerializer
from caretakers.serializers.delete import CaregiverRemoveSerializer

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from accounts.details.details_serializers import UserProfileGetSerializer, HealthInfoGetSerializer
from medications.models import Medicine, Intake
from medications.serializers import MedicineSerializer, IntakeSerializer


class IsOwnerUser(permissions.BasePermission):
    """
    Object-level permission: only the 'user' (the cared-for person) can access/modify a record.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user_id", None) == request.user.id


class OwnerQuerysetMixin:
    """Common: ensure queryset is scoped and uses select_related for efficiency."""

    def get_base_queryset(self):
        return CareGivers.objects.select_related("user", "caregiver")


class CaregiverListCreateAPIView(OwnerQuerysetMixin, generics.ListCreateAPIView):
    """
    GET  /caretakers/           -> caregivers added for the current user
    POST /caretakers/           -> add a caregiver for the current user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_base_queryset().filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CaregiverCreateSerializer
        return CaregiverDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CaregiverRetrieveUpdateDestroyAPIView(
    OwnerQuerysetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    GET    /caretakers/{pk}/    -> detail (only if owned by current user)
    PATCH  /caretakers/{pk}/    -> update contact info (only owned)
    DELETE /caretakers/{pk}/    -> remove caregiver (only owned)
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerUser]

    def get_queryset(self):
        return self.get_base_queryset().filter(user=self.request.user)

    def get_serializer_class(self):
        method = self.request.method
        if method in ("PUT", "PATCH"):
            return CaregiverUpdateSerializer
        if method == "DELETE":
            return CaregiverRemoveSerializer
        return CaregiverDetailSerializer


class CaregiverAsCaregiverListAPIView(OwnerQuerysetMixin, generics.ListAPIView):
    """
    GET /caretakers/as-caregiver/ -> list all CareGivers entries where current user is the caregiver
    (i.e., users for whom the current user provides care)
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CaregiverDetailSerializer

    def get_queryset(self):
        return self.get_base_queryset().filter(caregiver=self.request.user)


class CaregiverPatientDetailAPIView(APIView):
    """
    GET /caretakers/patient/{pk}/ -> Get full details of a patient (user)
    Only accessible if the current user is a registered caretaker for that patient.
    Aggregates profile, health info, medicines, and recent intakes.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, format=None):
        # 1. Verify that 'request.user' is a caregiver for 'user with id=pk'
        try:
            care_relation = CareGivers.objects.get(caregiver=request.user, user_id=pk)
        except CareGivers.DoesNotExist:
            return Response(
                {"detail": "You are not authorized to view this patient's details."},
                status=status.HTTP_403_FORBIDDEN
            )

        target_user = care_relation.user

        # 2. Fetch Profile & Health Info
        profile_data = {}
        if hasattr(target_user, 'profile'):
            # Context is needed for image URL generation
            profile_data = UserProfileGetSerializer(target_user.profile, context={'request': request}).data
            
        health_data = {}
        if hasattr(target_user, 'health_info'):
            health_data = HealthInfoGetSerializer(target_user.health_info).data

        # 3. Fetch Medicines
        medicines = Medicine.objects.filter(user=target_user)
        medicine_data = MedicineSerializer(medicines, many=True, context={'request': request}).data

        # 4. Fetch Recent Intakes (last 20 for history)
        intakes = Intake.objects.filter(user=target_user).order_by('-date', '-scheduled_time')[:20]
        intake_data = IntakeSerializer(intakes, many=True, context={'request': request}).data

        return Response({
            "profile": profile_data,
            "health_info": health_data,
            "medicines": medicine_data,
            "recent_intakes": intake_data
        })
