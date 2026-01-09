from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status
import logging

logger = logging.getLogger(__name__)


def global_exception_handler(exc, context):
    """
    Custom exception handler that preserves error details
    while maintaining consistent format.
    """
    # Get the standard DRF response
    response = exception_handler(exc, context)

    # If DRF handled it, that means it was `Http404` and `PermissionDenied` exceptions.
    if response is not None:
        return response

    # Handle unexpected exceptions (not caught by DRF)
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={"context": context},
    )

    # Return a generic error response
    return Response(
        {
            "detail": f"{exc.__class__.__name__} occurred.",
            "type": type(exc).__name__,
            "message": str(exc) if str(exc) else "Unknown error",
        },
        status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
