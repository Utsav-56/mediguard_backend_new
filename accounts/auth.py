from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Check the cookie first
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None

        if raw_token is None:
            # If no cookie, check the header
            header = self.get_header(request)
            raw_token = self.get_raw_token(header) if header is not None else None

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)  # type: ignore
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            # If token is invalid, return None instead of raising exception
            # This allows AllowAny views to work even with invalid tokens
            return None
