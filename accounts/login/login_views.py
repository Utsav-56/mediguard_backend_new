from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.login.login_serializers import UserLoginSerializer
from accounts.utils import delete_auth_cookies, set_auth_cookies


class UserLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(
                {
                    "detail": "You are already authenticated.",
                },
                status=HTTP_400_BAD_REQUEST,
            )

        response = super().post(request, *args, **kwargs)
        print(f"Login response data: {response.data}")

        # Set the JWT token in an HttpOnly cookie
        if response.status_code == HTTP_200_OK:
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            response = set_auth_cookies(response, access_token, refresh_token)

        return response


class LogoutView(APIView):
    """API view to log out the user by clearing auth cookies"""

    def post(self, request):
        response = Response({"detail": "Logged out successfully."}, status=HTTP_200_OK)
        # Clear the auth cookies
        response = delete_auth_cookies(response)
        return response
