"""Custom exception hierarchy for augint-library.

This module provides a comprehensive exception hierarchy with:
- Structured error data with error codes
- JSON serialization support
- Fluent interface for adding context
- Decorators for exception handling
- Testing utilities
"""

import json
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import Any, Callable, Optional


class ErrorCode(Enum):
    """Enumeration of error codes for consistent error handling."""

    GENERIC_ERROR = "GENERIC_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    NETWORK_ERROR = "NETWORK_ERROR"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    MULTIPLE_ERRORS = "MULTIPLE_ERRORS"


class AugintError(Exception):
    """Base exception class for all augint-library errors.

    Features:
    - Error codes for categorization
    - Structured error details
    - JSON serialization
    - Fluent interface for context
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.GENERIC_ERROR,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize AugintError.

        Args:
            message: Human-readable error message
            code: Error code for categorization
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc)

    def with_code(self, code: ErrorCode) -> "AugintError":
        """Set error code (fluent interface)."""
        self.code = code
        return self

    def with_detail(self, key: str, value: Any) -> "AugintError":
        """Add a detail (fluent interface)."""
        self.details[key] = value
        return self

    def with_context(self, context: dict[str, Any]) -> "AugintError":
        """Add multiple details (fluent interface)."""
        self.details.update(context)
        return self

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert exception to JSON string."""
        return json.dumps({"error": self.to_dict()}, default=str)


class ConfigurationError(AugintError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize ConfigurationError.

        Args:
            message: Error message
            key: Configuration key that caused the error
            **kwargs: Additional details
        """
        details = {"key": key} if key else {}
        details.update(kwargs)
        super().__init__(message, ErrorCode.CONFIGURATION_ERROR, details)


class ValidationError(AugintError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        constraint: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize ValidationError.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            constraint: Constraint that was violated
            **kwargs: Additional details
        """
        details = {}
        if field is not None:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if constraint is not None:
            details["constraint"] = constraint
        details.update(kwargs)
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)

    @classmethod
    def create_mock(cls, **kwargs: Any) -> "ValidationError":
        """Create a mock ValidationError for testing."""
        message = kwargs.pop("message", "Mock validation error")
        return cls(message, **kwargs)


class ResourceError(AugintError):
    """Base class for resource-related errors."""

    def __init__(
        self, message: str, code: ErrorCode, resource_type: str, resource_id: Any, **kwargs: Any
    ) -> None:
        """Initialize ResourceError."""
        details = {"resource_type": resource_type, "resource_id": resource_id}
        details.update(kwargs)
        super().__init__(message, code, details)


class ResourceNotFoundError(ResourceError):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: Any, **kwargs: Any) -> None:
        """Initialize ResourceNotFoundError."""
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(
            message, ErrorCode.RESOURCE_NOT_FOUND, resource_type, resource_id, **kwargs
        )


class ResourceAlreadyExistsError(ResourceError):
    """Raised when trying to create a resource that already exists."""

    def __init__(self, resource_type: str, resource_id: Any, **kwargs: Any) -> None:
        """Initialize ResourceAlreadyExistsError."""
        message = f"{resource_type} with id {resource_id} already exists"
        super().__init__(
            message, ErrorCode.RESOURCE_ALREADY_EXISTS, resource_type, resource_id, **kwargs
        )


class NetworkError(AugintError):
    """Base class for network-related errors."""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.NETWORK_ERROR,
        service: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize NetworkError."""
        details = {"service": service} if service else {}
        details.update(kwargs)
        super().__init__(message, code, details)


class NetworkTimeoutError(NetworkError):
    """Raised when a network operation times out."""

    def __init__(self, service: str, timeout: float, **kwargs: Any) -> None:
        """Initialize NetworkTimeoutError."""
        message = f"Timeout connecting to {service} after {timeout}s"
        super().__init__(
            message, ErrorCode.NETWORK_TIMEOUT, service=service, timeout=timeout, **kwargs
        )


class RateLimitError(NetworkError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        service: str,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize RateLimitError."""
        message = f"Rate limit exceeded for {service}"
        if retry_after:
            message += f", retry after {retry_after}s"

        # Add rate limit details to kwargs
        if retry_after is not None:
            kwargs["retry_after"] = retry_after
        if limit is not None:
            kwargs["limit"] = limit
        if remaining is not None:
            kwargs["remaining"] = remaining

        super().__init__(message, ErrorCode.RATE_LIMIT_EXCEEDED, service=service, **kwargs)


class MultiError(AugintError):
    """Container for multiple errors in batch operations."""

    def __init__(self, errors: list[AugintError]):
        """Initialize MultiError.

        Args:
            errors: List of errors that occurred
        """
        self.errors = errors
        message = f"{len(errors)} errors occurred"
        super().__init__(message, ErrorCode.MULTIPLE_ERRORS)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary including all errors."""
        base_dict = super().to_dict()
        base_dict["errors"] = [error.to_dict() for error in self.errors]
        return base_dict


def handle_exceptions(exception_map: dict[type[Exception], ErrorCode]) -> Callable[..., Any]:
    """Decorator to transform standard exceptions to AugintError.

    Args:
        exception_map: Mapping of exception types to error codes

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except AugintError:
                # Re-raise our own exceptions
                raise
            except Exception as e:
                # Transform mapped exceptions
                for exc_type, error_code in exception_map.items():
                    if isinstance(e, exc_type):
                        raise AugintError(str(e), code=error_code) from e
                # Re-raise unmapped exceptions
                raise

        return wrapper

    return decorator


def collect_errors(func: Callable[..., Any]) -> Callable[..., tuple[Any, list[AugintError]]]:
    """Decorator to collect errors in batch operations.

    Returns tuple of (results, errors) instead of raising.

    Args:
        func: Function to decorate

    Returns:
        Decorated function returning (results, errors)
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, list[AugintError]]:
        errors = []
        results = []

        # Get the first argument (assumed to be iterable)
        if not args:
            return func(*args, **kwargs), []

        items = args[0]
        remaining_args = args[1:]

        for item in items:
            try:
                # Call function with individual item
                result = func([item], *remaining_args, **kwargs)
                results.extend(result if isinstance(result, list) else [result])
            except AugintError as e:
                errors.append(e)
            except Exception as e:
                # Wrap non-AugintError exceptions
                errors.append(AugintError(str(e)))

        return results, errors

    return wrapper


def error_context(**context: Any) -> Callable[..., Any]:
    """Decorator to add context to any exceptions raised.

    Args:
        **context: Context to add to exceptions

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except AugintError as e:
                # Add context to our exceptions
                e.with_context(context)
                raise
            except Exception:
                # Don't modify other exceptions
                raise

        return wrapper

    return decorator
