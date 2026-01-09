from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    BloodPressure, BloodSugar, Cholestrol, HeartRate, GenericMetric
)
from .serializers import (
    BloodPressureSerializer, BloodSugarSerializer, 
    CholestrolSerializer, HeartRateSerializer, GenericMetricSerializer
)

class BaseMetricViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'updated_at': ['gt', 'lt', 'gte', 'lte'],
        'is_deleted': ['exact'],
        'timestamp': ['gt', 'lt', 'gte', 'lte'],
    }

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class BloodPressureViewSet(BaseMetricViewSet):
    model = BloodPressure
    queryset = BloodPressure.objects.all()
    serializer_class = BloodPressureSerializer

class BloodSugarViewSet(BaseMetricViewSet):
    model = BloodSugar
    queryset = BloodSugar.objects.all()
    serializer_class = BloodSugarSerializer

class CholestrolViewSet(BaseMetricViewSet):
    model = Cholestrol
    queryset = Cholestrol.objects.all()
    serializer_class = CholestrolSerializer

class HeartRateViewSet(BaseMetricViewSet):
    model = HeartRate
    queryset = HeartRate.objects.all()
    serializer_class = HeartRateSerializer

class GenericMetricViewSet(BaseMetricViewSet):
    model = GenericMetric
    queryset = GenericMetric.objects.all()
    serializer_class = GenericMetricSerializer
    filterset_fields = {
        **BaseMetricViewSet.filterset_fields,
        'metric_name': ['exact', 'icontains'],
    }
