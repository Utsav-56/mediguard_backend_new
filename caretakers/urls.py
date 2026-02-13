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
        "patient/<int:patient_id>/",
        views.PatientFullDetailsView.as_view(),
        name="patient-full-details",
    ),
    path(
        "patient/<int:patient_id>/update/",
        views.PatientUpdateView.as_view(),
        name="patient-update",
    ),
]
