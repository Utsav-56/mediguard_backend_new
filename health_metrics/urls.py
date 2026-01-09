from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BloodPressureViewSet, BloodSugarViewSet, 
    CholestrolViewSet, HeartRateViewSet, GenericMetricViewSet
)

router = DefaultRouter()
router.register(r'blood-pressure', BloodPressureViewSet, basename='bloodpressure')
router.register(r'blood-sugar', BloodSugarViewSet, basename='bloodsugar')
router.register(r'cholestrol', CholestrolViewSet, basename='cholestrol')
router.register(r'heart-rate', HeartRateViewSet, basename='heartrate')
router.register(r'generic-metrics', GenericMetricViewSet, basename='genericmetric')

urlpatterns = [
    path('', include(router.urls)),
]
