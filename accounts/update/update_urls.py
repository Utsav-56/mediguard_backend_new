from django.urls import path
from accounts.update.update_views import UserUpdateView, PasswordChangeView

urlpatterns = [
    path("update/", view=UserUpdateView.as_view(), name="user_update"),
    path("change-password/", view=PasswordChangeView.as_view(), name="change_password"),
]
