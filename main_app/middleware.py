# ONLY standard python imports at the top
from urllib.parse import parse_qs


class WebSocketJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # MOVE ALL THESE INSIDE
        from django.contrib.auth.models import AnonymousUser
        from django.conf import settings
        from channels.db import database_sync_to_async
        from rest_framework_simplejwt.tokens import AccessToken
        from accounts.models import User

        @database_sync_to_async
        def get_user(token_key):
            try:
                access_token = AccessToken(token_key)
                user = User.objects.get(id=access_token["user_id"])
                return user
            except Exception:
                return AnonymousUser()

        # --- Your Token Logic ---
        headers = dict(scope["headers"])
        cookies_header = headers.get(b"cookie", b"").decode()

        cookies = {}
        if cookies_header:
            for cookie in cookies_header.split("; "):
                parts = cookie.split("=")
                if len(parts) == 2:
                    cookies[parts[0]] = parts[1]

        token = None
        auth_cookie_name = getattr(settings, "SIMPLE_JWT", {}).get("AUTH_COOKIE")
        if auth_cookie_name and auth_cookie_name in cookies:
            token = cookies[auth_cookie_name]

        if not token and b"authorization" in headers:
            auth_header = headers[b"authorization"].decode()
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            query_string = scope.get("query_string", b"").decode()
            query_params = parse_qs(query_string)
            if "token" in query_params:
                token = query_params["token"][0]

        if token:
            scope["user"] = await get_user(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
