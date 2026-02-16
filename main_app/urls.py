"""
URL configuration for main_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.http.response import HttpResponse

from django.contrib import admin
from django.urls import path, include

from utils.views import DownloadDatabaseView, PingView

urlpatterns = [
    path("ping/", PingView.as_view(), name="ping"),
    path("db-download/", DownloadDatabaseView.as_view(), name="db_download"),
    path("admin/", admin.site.urls),
    path("auth/", include("accounts.urls")),
    path("accounts/", include("accounts.urls")),
    path("notifications/", include("notifications.urls")),
    # path("medications/", include("medications.urls")),
    # path("health-metrics/", include("health_metrics.urls")),
    path("caretakers/", include("caretakers.urls")),
    # just say hello from mediguard in /
    path(
        "",
        lambda request: HttpResponse("""
        <h1>Welcome to MediGuard Backend!</h1>
        <p>This is the backend server for the MediGuard application.</p>
                                          <p style="font-style: italic;">Developed with care to manage your health data securely.</p>                                  
                                          
        <h1> Recent changes </h1>
        <p>Added sync mechanism and login mechanism</p>
                                          
                                          
                                          
                                          
                                          """),
    ),
]
