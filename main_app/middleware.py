import os
import django
from django.core.asgi import get_asgi_application

# 1. Set environment variable BEFORE anything else
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_app.settings")

# 2. Setup django
django.setup()

# 3. Initialize the ASGI application for HTTP
django_asgi_app = get_asgi_application()

# 4. NOW import the rest
from channels.routing import ProtocolTypeRouter, URLRouter
import main_app.routing
from main_app.middleware import WebSocketJWTAuthMiddleware

# 5. Define the final application
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketJWTAuthMiddleware(
            URLRouter(main_app.routing.websocket_urlpatterns)
        ),
    }
)
