from channels.db import database_sync_to_async

# ❌ REMOVED: from django.contrib.auth.models import AnonymousUser
# ❌ REMOVED: from accounts.models import User
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings
from urllib.parse import parse_qs


@database_sync_to_async
def get_user(token_key):
    # ✅ MOVED INSIDE
    from django.contrib.auth.models import AnonymousUser
    from accounts.models import User

    try:
        access_token = AccessToken(token_key)
        user = User.objects.get(id=access_token["user_id"])
        return user
    except Exception as e:
        return AnonymousUser()


class WebSocketJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # ✅ MOVED INSIDE
        from django.contrib.auth.models import AnonymousUser

        # ... (rest of your logic remains the same) ...

        if token:
            scope["user"] = await get_user(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
