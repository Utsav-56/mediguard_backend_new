import os
import django
from django.core.asgi import get_asgi_application

# 1. Set the settings module first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_app.settings")

# 2. Initialize the Django ASGI application FIRST.
# This loads all INSTALLED_APPS and models.
django_asgi_app = get_asgi_application()

# 3. NOW it is safe to import your project-specific code.
from channels.routing import ProtocolTypeRouter, URLRouter
from main_app.middleware import WebSocketJWTAuthMiddleware
import main_app.routing

# 4. Define the final application
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketJWTAuthMiddleware(
            URLRouter(main_app.routing.websocket_urlpatterns)
        ),
    }
)
