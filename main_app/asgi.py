import os
from django.core.asgi import get_asgi_application

# 1. Set settings first
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_app.settings")

# 2. Initialize the Django ASGI application early.
# This "wakes up" Django so models/settings can be accessed.
django_asgi_app = get_asgi_application()

# 3. NOW you can import your custom code
from channels.routing import ProtocolTypeRouter, URLRouter
import main_app.routing
from main_app.middleware import WebSocketJWTAuthMiddleware

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketJWTAuthMiddleware(
            URLRouter(main_app.routing.websocket_urlpatterns)
        ),
    }
)
