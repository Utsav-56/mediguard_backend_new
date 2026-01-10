from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .auth import set_auth_cookies, clear_auth_cookies
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserCreateSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
)


class SignupView(generics.CreateAPIView):
    """
    Handles user registration and creates a profile automatically.
    """

    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(
                {"detail": "User is already logged in."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-login: Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "message": "User created successfully",
                "user": user.get_user_info(),
            },
            status=status.HTTP_201_CREATED,
        )

        set_auth_cookies(response, access_token, refresh_token)

        return response


class CustomTokenObtainView(TokenObtainPairView):
    """
    Login view that sets tokens in HTTP-only cookies and returns user info.
    No tokens are sent in the response body.
    """

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(
                {"detail": "User is already logged in."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            # Extract and remove tokens from body
            access_token = response.data.pop("access")
            refresh_token = response.data.pop("refresh")
            set_auth_cookies(response, access_token, refresh_token)

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Refreshes the access token via cookie and sets a new one.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.pop("access")
            refresh_token = (
                response.data.pop("refresh") if "refresh" in response.data else None
            )
            set_auth_cookies(response, access_token, refresh_token)

        return response


class CustomTokenVerifyView(APIView):
    """
    Verifies session and automatically refreshes tokens if access token is expired.
    Returns full user info.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        User = get_user_model()
        access_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])

        if access_token:
            try:
                token = AccessToken(access_token)
                user = User.objects.get(id=token["user_id"])
                return Response(
                    {"success": True, "refreshed": False, "user": user.get_user_info()}
                )
            except (TokenError, InvalidToken, User.DoesNotExist):
                # Access token failed, try refresh
                pass

        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)
                user = User.objects.get(id=refresh["user_id"])

                response = Response(
                    {"success": True, "refreshed": True, "user": user.get_user_info()}
                )

                new_refresh_token = (
                    str(refresh)
                    if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False)
                    else None
                )
                set_auth_cookies(response, new_access_token, new_refresh_token)
                return response
            except (TokenError, InvalidToken, User.DoesNotExist):
                pass

        return Response(
            {"detail": "Session expired or invalid. Please login again."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    """
    Clears authentication cookies on logout.
    """

    def post(self, request):
        response = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )
        clear_auth_cookies(response)
        return response


class ProfileView(APIView):
    """
    Retrieve and update user profile.
    Email change is not allowed.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": request.user.get_user_info()})

    def patch(self, request):
        # Prevent email change if it's in the payload
        # (Though UserProfileUpdateSerializer already excludes user field)
        try:
            profile = request.user.profile
        except Exception:
            # Handle case where profile might be missing (shouldn't happen with proper signup)
            from .models import UserProfile

            profile = UserProfile.objects.create(user=request.user)

        serializer = UserProfileUpdateSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile updated successfully.",
                    "user": request.user.get_user_info(),
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    Dedicated route for changing password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"detail": "Password changed successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
