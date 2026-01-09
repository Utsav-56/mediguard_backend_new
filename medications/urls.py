from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicineViewSet, IntakeViewSet

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'intakes', IntakeViewSet, basename='intake')

urlpatterns = [
    path('', include(router.urls)),
]
