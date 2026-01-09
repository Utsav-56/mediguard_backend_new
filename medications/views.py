from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medicine, Intake
from .serializers import MedicineSerializer, IntakeSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MedicineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'updated_at': ['gt', 'lt', 'gte', 'lte'],
        'is_deleted': ['exact'],
    }

    def get_queryset(self):
        return Medicine.objects.filter(user=self.request.user)

class IntakeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IntakeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'updated_at': ['gt', 'lt', 'gte', 'lte'],
        'is_deleted': ['exact'],
    }

    def get_queryset(self):
        return Intake.objects.filter(user=self.request.user)
