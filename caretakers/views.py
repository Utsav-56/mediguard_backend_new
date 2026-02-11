from rest_framework import generics, permissions

from caretakers.models import CareGivers
from caretakers.serializers.create import CaregiverCreateSerializer
from caretakers.serializers.update import CaregiverUpdateSerializer
from caretakers.serializers.read import CaregiverDetailSerializer
from caretakers.serializers.delete import CaregiverRemoveSerializer


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
