from django.urls import path
from caretakers import views

urlpatterns = [
    path("", views.CaregiverListCreateAPIView.as_view(), name="caretaker-list-create"),
    path(
        "as-caregiver/",
        views.CaregiverAsCaregiverListAPIView.as_view(),
        name="caretaker-as-caregiver",
    ),
    path(
        "<int:pk>/",
        views.CaregiverRetrieveUpdateDestroyAPIView.as_view(),
        name="caretaker-detail",
    ),
    path(
        "patient/<int:pk>/",
        views.CaregiverPatientDetailAPIView.as_view(),
        name="caretaker-patient-detail",
    ),
    path(
        "medicine/<uuid:pk>/",
        views.CaregiverMedicineDetailAPIView.as_view(),
        name="caretaker-medicine-detail",
    ),
]
