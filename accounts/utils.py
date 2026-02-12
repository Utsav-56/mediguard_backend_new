from django.conf import settings
from django.utils import timezone


def set_auth_cookies(response, access_token, refresh_token):
    """Set authentication cookies in the response"""
    access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

    # Calculate absolute expiration times
    access_expires = timezone.now() + access_lifetime
    refresh_expires = timezone.now() + refresh_lifetime

    # Set HttpOnly cookie for access token
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=access_token,
        expires=access_expires,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )

    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
        value=refresh_token,
        expires=refresh_expires,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )

    return response


def delete_auth_cookies(response):
    """Delete authentication cookies from the response"""
    response.delete_cookie(
        settings.SIMPLE_JWT["AUTH_COOKIE"], path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"]
    )
    response.delete_cookie(
        settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
        path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
    )
    return response
