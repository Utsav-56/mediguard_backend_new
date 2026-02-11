from django.urls import path
from accounts.register.register_views import UserCreateView

urlpatterns = [
    path("register/", view=UserCreateView.as_view(), name="signup"),
]
