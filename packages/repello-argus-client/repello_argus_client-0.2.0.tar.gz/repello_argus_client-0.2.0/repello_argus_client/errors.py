from typing import Any, Dict, Optional


class ArgusError(Exception):
    """The base class for all exceptions raised by the Argus SDK."""

    pass


class ArgusValueError(ArgusError):
    """Raised for client-side validation errors before an API call is made."""

    pass


class ArgusTypeError(ArgusValueError):
    """
    Raised for type mismatch errors in function arguments.
    Inherits from ArgusValueError.
    """

    pass


class ArgusConnectionError(ArgusError):
    """Raised for network-level issues preventing communication with the API."""

    pass


class ArgusAPIError(ArgusError):
    """
    The base class for errors returned by the API (HTTP status >= 400).

    Attributes:
        status_code (Optional[int]): The HTTP status code of the error response.
        response_body (Optional[dict]): The parsed JSON body of the error response.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            f"{message} (Status: {status_code})" if status_code else message
        )
        self.status_code = status_code
        self.response_body = response_body


class ArgusAuthenticationError(ArgusAPIError):
    """Raised for an HTTP 401 Unauthorized status."""

    pass


class ArgusPermissionError(ArgusAPIError):
    """Raised for an HTTP 403 Forbidden status."""

    pass


class ArgusNotFoundError(ArgusAPIError):
    """Raised for an HTTP 404 Not Found status."""

    pass


class ArgusInternalServerError(ArgusAPIError):
    """Raised for any HTTP 5xx server-side errors."""

    pass
