"""
ASGI config for main_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import main_app.routing
from main_app.middleware import WebSocketJWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_app.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": WebSocketJWTAuthMiddleware(
        URLRouter(
            main_app.routing.websocket_urlpatterns
        )
    ),
})
