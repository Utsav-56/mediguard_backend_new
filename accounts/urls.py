from django.urls import path
from accounts.views import (
    SignupView,
    CustomTokenObtainView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    ProfileView,
    PasswordChangeView,
)

urlpatterns = [
    # Auth
    path("register/", SignupView.as_view(), name="register"),
    path("signup/", SignupView.as_view(), name="signup"),  # Alias
    path("login/", CustomTokenObtainView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    
    # Session / Token management
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    path("session/verify/", CustomTokenVerifyView.as_view(), name="session_verify"), # Specific alias for session check
    
    # Profile management
    path("me/", ProfileView.as_view(), name="me"),
    path("me/update/", ProfileView.as_view(), name="me_update"),
    
    # Password management
    path("me/password/change/", PasswordChangeView.as_view(), name="password_change"),
]
