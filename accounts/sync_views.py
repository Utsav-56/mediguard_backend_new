from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from sync.utils import perform_sync

class GlobalSyncView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = perform_sync(request.user, request.data)
        return Response(result, status=status.HTTP_200_OK)
