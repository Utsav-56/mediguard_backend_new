from django.urls import path, include
from accounts.sync_views import GlobalSyncView

urlpatterns = [
    path("sync/", GlobalSyncView.as_view(), name="sync"),
    path("", include("accounts.register.register_urls")),
    path("", include("accounts.login.login_urls")),
    path("", include("accounts.details.details_urls")),
    path("", include("accounts.update.update_urls")),
]
