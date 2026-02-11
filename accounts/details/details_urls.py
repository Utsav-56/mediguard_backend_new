from django.urls import path
from accounts.details.details_views import LoggedUserInfoView

urlpatterns = [
    path("me/", view=LoggedUserInfoView.as_view(), name="logged_user_info"),
]
