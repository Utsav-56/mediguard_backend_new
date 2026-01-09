from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

class DeleteUserView(APIView):
    """
    View to delete the currently authenticated user's account.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        
        response = Response(
            {"detail": "Account deleted successfully."}, 
            status=status.HTTP_204_NO_CONTENT
        )
        
        # Clear cookies
        from django.conf import settings
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"],
            path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )
        
        return response
