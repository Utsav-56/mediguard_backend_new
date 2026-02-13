from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from rest_framework.response import Response
from rest_framework.views import APIView


class LoggedUserInfoView(APIView):
    """API view to get logged in user info"""

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=HTTP_400_BAD_REQUEST,
            )

        from accounts.details.details_serializers import CompleteUserGetSerializer
        return Response(
            {"user": CompleteUserGetSerializer(user, context={"request": request}).data},
            status=HTTP_200_OK,
        )
