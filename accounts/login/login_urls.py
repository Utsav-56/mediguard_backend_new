from django.urls import path
from accounts.login.login_views import UserLoginView, LogoutView

urlpatterns = [
    path("login/", view=UserLoginView.as_view(), name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
]
