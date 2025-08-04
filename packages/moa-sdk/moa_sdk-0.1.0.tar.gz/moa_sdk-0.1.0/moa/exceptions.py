"""Custom exceptions for MOA SDK."""

from typing import Any, Dict, Optional


class MOAError(Exception):
    """Base exception for all MOA SDK errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MOAAPIError(MOAError):
    """Exception raised for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}


class MOAAuthError(MOAAPIError):
    """Exception raised for authentication errors."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class MOAConnectionError(MOAError):
    """Exception raised for connection-related errors."""

    pass


class MOATimeoutError(MOAError):
    """Exception raised for timeout errors."""

    pass


class MOAValidationError(MOAError):
    """Exception raised for validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field


class MOARateLimitError(MOAAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class MOANotFoundError(MOAAPIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class MOAServerError(MOAAPIError):
    """Exception raised for server errors (5xx)."""

    def __init__(self, message: str = "Internal server error", **kwargs):
        super().__init__(message, **kwargs)
