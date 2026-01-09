from django.urls import path
from djoser.views import UserViewSet

from accounts.views import (
    CustomTokenObtainView,
    CustomTokenRefreshView,
    LogoutView,
    CustomTokenVerifyView,
)
from accounts.update.views import (
    UpdateProfilePictureView,
    ProfileUpdateView,
    PasswordUpdateView,
    FirstNameUpdateView,
)

urlpatterns = [
    path(
        "me/", UserViewSet.as_view({"get": "me", "put": "me", "patch": "me"}), name="me"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "update/profile_pic/",
        UpdateProfilePictureView.as_view(),
        name="update_profile_pic",
    ),
    path("update/", ProfileUpdateView.as_view(), name="update_profile"),
    path("update/password/", PasswordUpdateView.as_view(), name="update_password"),
    path("update/first_name/", FirstNameUpdateView.as_view(), name="update_first_name"),
]
