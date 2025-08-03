"""
Custom exception hierarchy for the pyjupiter package.

This module defines a comprehensive set of exceptions that provide
better error handling and debugging capabilities for Jupiter API interactions.
"""

from typing import Any, Optional


class JupiterError(Exception):
    """
    Base exception class for all Jupiter-related errors.

    This is the root exception that all other Jupiter exceptions inherit from.
    Use this for general exception handling when you want to catch any Jupiter error.
    """

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """
        Initialize the base Jupiter error.

        Args:
            message: Human-readable error message.
            details: Optional additional error details.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class JupiterAPIError(JupiterError):
    """
    Exception raised for API-related errors.

    This exception includes HTTP status codes and response data
    for better debugging of API issues.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the API error.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code from the API response.
            response_data: Raw response data from the API.
            details: Optional additional error details.
        """
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}


class JupiterNetworkError(JupiterError):
    """
    Exception raised for network connectivity issues.

    This includes timeouts, connection errors, DNS resolution failures,
    and other network-related problems.
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize the network error.

        Args:
            message: Human-readable error message.
            original_error: The original exception that caused this error.
        """
        super().__init__(message)
        self.original_error = original_error


class JupiterRateLimitError(JupiterAPIError):
    """
    Exception raised when API rate limits are exceeded.

    This exception extends JupiterAPIError and includes retry timing information.
    """

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the rate limit error.

        Args:
            message: Human-readable error message.
            retry_after: Number of seconds to wait before retrying.
            status_code: HTTP status code (typically 429).
            response_data: Raw response data from the API.
        """
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class JupiterValidationError(JupiterError):
    """
    Exception raised for input validation errors.

    This includes invalid parameters, malformed data,
    missing required fields, and other validation failures.
    """

    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        """
        Initialize the validation error.

        Args:
            message: Human-readable error message.
            field: The field that failed validation.
            value: The invalid value that caused the error.
        """
        super().__init__(message)
        self.field = field
        self.value = value


class JupiterAuthenticationError(JupiterAPIError):
    """
    Exception raised for authentication and authorization errors.

    This includes invalid API keys, expired tokens,
    insufficient permissions, and other auth-related issues.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the authentication error.

        Args:
            message: Human-readable error message.
            status_code: HTTP status code (typically 401 or 403).
            response_data: Raw response data from the API.
        """
        super().__init__(message, status_code, response_data)
