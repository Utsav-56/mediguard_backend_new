from django.urls import path
from .views import SyncMapView

urlpatterns = [
    path('map/', SyncMapView.as_view(), name='sync_map'),
]
