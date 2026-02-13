from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.update.update_serializers import PasswordUpdateSerializer, UserUpdateSerializer
from accounts.details.details_serializers import CompleteUserGetSerializer


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
            {"user": CompleteUserGetSerializer(user, context={"request": request}).data}, status=HTTP_200_OK
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
