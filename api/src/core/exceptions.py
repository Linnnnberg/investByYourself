#!/usr/bin/env python3
"""
InvestByYourself API Exception Handling
Tech-028: API Implementation

Custom exception classes and error handling for the API.
"""

from typing import Any, Dict, Optional


class APIException(Exception):
    """Base API exception class."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIException):
    """Validation error exception."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationError(APIException):
    """Authentication error exception."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(APIException):
    """Authorization error exception."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class NotFoundError(APIException):
    """Resource not found error exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, status_code=404, error_code="NOT_FOUND", details=details
        )


class ConflictError(APIException):
    """Resource conflict error exception."""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message, status_code=409, error_code="CONFLICT", details=details
        )


class RateLimitError(APIException):
    """Rate limit exceeded error exception."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


class ExternalAPIError(APIException):
    """External API error exception."""

    def __init__(
        self,
        message: str = "External API error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=502,
            error_code="EXTERNAL_API_ERROR",
            details=details,
        )


class DatabaseError(APIException):
    """Database error exception."""

    def __init__(
        self, message: str = "Database error", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


class CacheError(APIException):
    """Cache error exception."""

    def __init__(
        self, message: str = "Cache error", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message, status_code=500, error_code="CACHE_ERROR", details=details
        )
