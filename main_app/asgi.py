import os
from django.core.asgi import get_asgi_application

# 1. Set settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main_app.settings")

# 2. Initialize Django ASGI application
# This MUST happen before importing any middleware or routing
django_asgi_app = get_asgi_application()

# 3. Import Channels components AFTER get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter


# This function handles the "lazy" loading of your routing/middleware
def get_project_application():
    import main_app.routing
    from main_app.middleware import WebSocketJWTAuthMiddleware

    return ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": WebSocketJWTAuthMiddleware(
                URLRouter(main_app.routing.websocket_urlpatterns)
            ),
        }
    )


application = get_project_application()
