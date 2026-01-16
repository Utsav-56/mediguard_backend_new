from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers.create import UserSignupSerializer
from accounts.serializers.login import UserLoginSerializer
from accounts.serializers.read import CompleteUserGetSerializer
from accounts.serializers.update import PasswordUpdateSerializer, UserUpdateSerializer
from accounts.utils import delete_auth_cookies, set_auth_cookies


# An api endpoint for creating a user
class UserCreateView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {
                    "detail": "You are already authenticated.",
                },
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = UserSignupSerializer(data=request.data)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        # try:
        user = serializer.save()
        return Response(
            {
                "user": CompleteUserGetSerializer(
                    user, context={"request": request}
                ).data
            },
            status=HTTP_201_CREATED,
        )


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


class LoggedUserInfoView(APIView):
    """API view to get logged in user info"""

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=HTTP_400_BAD_REQUEST,
            )

        return Response({"user": user.full_info}, status=HTTP_200_OK)


class UserUpdateView(APIView):
    """API view to update logged in user info"""

    def put(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(
            {"user": CompleteUserGetSerializer(user).data}, status=HTTP_200_OK
        )


class PasswordChangeView(APIView):
    """API view to change logged in user password"""

    def put(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "You are not logged in."},
                status=HTTP_400_BAD_REQUEST,
            )

        serializer = PasswordUpdateSerializer(
            user, data=request.data, partial=True, context={"request": request}
        )

        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response(
            {"detail": "Password updated successfully."}, status=HTTP_200_OK
        )


class LogoutView(APIView):
    """API view to log out the user by clearing auth cookies"""

    def post(self, request):
        response = Response({"detail": "Logged out successfully."}, status=HTTP_200_OK)
        # Clear the auth cookies
        response = delete_auth_cookies(response)
        return response
