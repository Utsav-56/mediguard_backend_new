"""
This module contains views for updating user profiles in the accounts application.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from accounts.update.serializers import (
    ProfilePictureUpdateSerializer,
    PasswordUpdateSerializer,
    FirstNameUpdateSerializer,
)
from accounts.serializers import UserSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class ProfileUpdateView(APIView):
    """
    View to handle full or partial updates to user profile.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request):
        """
        Handle full update of user profile.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """
        Handle partial update of user profile.
        """
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePictureUpdateView(APIView):
    """
    View to handle updating the profile picture separately.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Handle profile picture update only.
        """
        user = request.user
        serializer = ProfilePictureUpdateSerializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordUpdateView(APIView):
    """
    View to handle updating the user's password.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Handle password update with current password verification.
        """
        user = request.user
        serializer = PasswordUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FirstNameUpdateView(APIView):
    """
    View to handle updating the user's first name.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Handle first name update only.
        """
        user = request.user
        serializer = FirstNameUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfilePictureView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        return self._update_picture(request)

    def patch(self, request):
        return self._update_picture(request)

    def _update_picture(self, request):
        serializer = ProfilePictureUpdateSerializer(
            request.user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Profile picture updated successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
