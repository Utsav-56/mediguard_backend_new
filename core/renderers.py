from rest_framework.renderers import JSONRenderer


class GlobalResponseRenderer(JSONRenderer):
    """
    Converts all API responses into a consistent {success, response, error} format.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code
        is_success = 200 <= status_code < 300

        # Check if already wrapped in SRE format
        if self._is_already_wrapped(data):
            return super().render(data, accepted_media_type, renderer_context)

        # Handle success responses
        if is_success:
            wrapped_data = {
                "success": True,
                "response": data if data is not None else {},
                "error": None,
            }
        # Handle error responses
        else:
            error_field = self._extract_error_details(data)
            # add status code to error field for backward compatibility
            # also add a field called 'reached_server' to indicate that the request reached the server

            error_field["status"] = status_code
            error_field["reached_server"] = True
            wrapped_data = {
                "success": False,
                "response": None,
                "error": error_field,
            }

        # before sending lets add reached_server to top level for backward compatibility
        wrapped_data["reached_server"] = True

        # also add the user id as requesting_user_id if user is authenticated
        request = renderer_context.get("request")
        if request and request.user.is_authenticated:
            wrapped_data["requesting_user_id"] = request.user.id
        else:
            wrapped_data["requesting_user_id"] = None

        return super().render(wrapped_data, accepted_media_type, renderer_context)

    def _is_already_wrapped(self, data):
        """Check if data is already in SRE format."""
        return (
            isinstance(data, dict)
            and "success" in data
            and ("response" in data or "error" in data)
        )

    def _extract_error_details(self, data):
        """Extract and standardize error details from various formats."""
        # If already properly formatted error
        if isinstance(data, dict) and all(
            key in data for key in ("type", "message", "message_type")
        ):
            return data

        error_field = {
            "type": "unknown_error",
            "message": None,
            "message_type": None,
        }

        # Handle dict data
        if isinstance(data, dict):
            # Check for DRF 'detail' key
            if "detail" in data:
                error_field["message"] = data["detail"]
                error_field["message_type"] = type(data["detail"]).__name__
            # Check for custom error/errors keys
            elif "error" in data:
                error_field["message"] = data["error"]
                error_field["message_type"] = type(data["error"]).__name__
            elif "errors" in data:
                error_field["message"] = data["errors"]
                error_field["message_type"] = type(data["errors"]).__name__
            # Validation errors (field-level errors)
            else:
                error_field["type"] = "ValidationError"
                error_field["message"] = self._normalize_validation_errors(data)
                error_field["message_type"] = "dict"
        # Handle list data
        elif isinstance(data, list):
            error_field["message"] = data
            error_field["message_type"] = "list"
        # Handle string/other data
        else:
            error_field["message"] = str(data) if data else "An error occurred"
            error_field["message_type"] = "str"

        return error_field

    def _normalize_validation_errors(self, data):
        """Convert ErrorDetail objects to strings in validation errors."""
        normalized = {}
        for key, value in data.items():
            if isinstance(value, list):
                normalized[key] = [str(item) for item in value]
            else:
                normalized[key] = str(value)
        return normalized
