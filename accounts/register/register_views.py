from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.register.register_serializers import UserSignupSerializer
from accounts.details.details_serializers import CompleteUserGetSerializer


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
