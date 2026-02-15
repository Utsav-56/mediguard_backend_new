from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from accounts.models import User
from django.conf import settings
from urllib.parse import parse_qs

@database_sync_to_async
def get_user(token_key):
    try:
        access_token = AccessToken(token_key)
        user = User.objects.get(id=access_token['user_id'])
        return user
    except Exception as e:
        return AnonymousUser()

class WebSocketJWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look for token in headers or cookies
        headers = dict(scope['headers'])
        cookies_header = headers.get(b'cookie', b'').decode()
        
        cookies = {}
        if cookies_header:
            for cookie in cookies_header.split('; '):
                parts = cookie.split('=')
                if len(parts) == 2:
                    cookies[parts[0]] = parts[1]
        
        token = None
        # Try to get token from cookie
        auth_cookie_name = getattr(settings, 'SIMPLE_JWT', {}).get('AUTH_COOKIE')
        if auth_cookie_name and auth_cookie_name in cookies:
            token = cookies[auth_cookie_name]
        
        # If not in cookie, check Authorization header
        if not token and b'authorization' in headers:
            auth_header = headers[b'authorization'].decode()
            if auth_header.startswith('Bearer '):
               token = auth_header.split(' ')[1]

        # If still not found, check query params (fallback)
        if not token:
            query_string = scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            if 'token' in query_params:
                token = query_params['token'][0]

        if token:
            scope['user'] = await get_user(token)
        else:
            scope['user'] = AnonymousUser()
        
        return await self.app(scope, receive, send)
