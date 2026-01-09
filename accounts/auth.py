from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Check the header first
        header = self.get_header(request)

        if header is None:
            # If no header, check the cookie
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            # If token is invalid, return None instead of raising exception
            # This allows AllowAny views to work even with invalid tokens
            return None


def set_auth_cookies(response, access_token=None, refresh_token=None):
    """
    Sets authentication tokens in HTTP-only cookies.
    """
    if access_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
        )
    if refresh_token:
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
            value=refresh_token,
            expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
        )


def clear_auth_cookies(response):
    """
    Removes authentication cookies.
    """
    cookie_keys = [
        settings.SIMPLE_JWT["AUTH_COOKIE"],
        settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
    ]
    for key in cookie_keys:
        response.delete_cookie(
            key=key,
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
        )
