from django.urls import path, include

urlpatterns = [
    path("", include("accounts.register.register_urls")),
    path("", include("accounts.login.login_urls")),
    path("", include("accounts.details.details_urls")),
    path("", include("accounts.update.update_urls")),
]
