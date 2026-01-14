from django.contrib.auth.views import LogoutView
from accounts.views import (
    PasswordChangeView,
    UserCreateView,
    UserLoginView,
    LoggedUserInfoView,
    UserUpdateView,
)

from django.urls import path


urlpatterns = [
    path("register/", view=UserCreateView.as_view(), name="signup"),
    path("login/", view=UserLoginView.as_view(), name="login"),
    path("me/", view=LoggedUserInfoView.as_view(), name="logged_user_info"),
    path("update/", view=UserUpdateView.as_view(), name="user_update"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("change-password/", view=PasswordChangeView.as_view(), name="change_password"),
]
