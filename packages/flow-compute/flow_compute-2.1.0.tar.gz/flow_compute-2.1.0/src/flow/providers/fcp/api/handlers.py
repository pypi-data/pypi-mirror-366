"""Error handling utilities for FCP provider.

This module provides decorators and utilities for consistent error handling
across FCP operations.
"""

import functools
import logging
from typing import Any, Callable, TypeVar

from flow.errors import FlowError, TimeoutError as FlowTimeoutError

from ..core.errors import (
    FCPAPIError,
    FCPAuthenticationError,
    FCPError,
    FCPQuotaExceededError,
    FCPResourceNotFoundError,
    FCPTimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


def handle_fcp_errors(operation: str = "FCP operation") -> Callable:
    """Decorator to handle FCP-specific errors with proper logging and conversion.

    Args:
        operation: Description of the operation for error messages

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except FCPError:
                # Already a specific FCP error (including FCPAPIError, FCPInstanceError, etc), re-raise
                raise
            except (TimeoutError, FlowTimeoutError) as e:
                # Handle timeout errors first (before FlowError)
                raise FCPTimeoutError(f"{operation} timed out") from e
            except FlowError as e:
                # Check if this is an HTTP error we can convert
                if hasattr(e, "status_code"):
                    status_code = e.status_code
                    response_body = getattr(e, "response_body", None)

                    # Convert to specific FCP errors based on status code
                    if status_code == 401:
                        raise FCPAuthenticationError(
                            f"{operation} failed: Authentication required",
                            status_code=status_code,
                            response_body=response_body,
                        ) from e
                    elif status_code == 404:
                        raise FCPResourceNotFoundError(
                            str(e) or f"{operation} failed: Resource not found",
                            status_code=status_code,
                            response_body=response_body,
                        ) from e
                    elif status_code == 429:
                        raise FCPQuotaExceededError(
                            f"{operation} failed: Rate limit or quota exceeded",
                            status_code=status_code,
                            response_body=response_body,
                        ) from e
                    elif status_code and status_code >= 500:
                        raise FCPAPIError(
                            f"{operation} failed: Server error",
                            status_code=status_code,
                            response_body=response_body,
                        ) from e

                # Re-raise other Flow errors
                raise
            except Exception as e:
                # Handle httpx network errors
                if hasattr(e, "__class__") and e.__class__.__name__ in [
                    "NetworkError",
                    "ConnectError",
                    "ConnectTimeout",
                ]:
                    from flow.errors import NetworkError

                    raise NetworkError(
                        f"{operation} failed: {str(e)}",
                        suggestions=[
                            "Check your internet connection",
                            "Verify the API endpoint is correct",
                            "Check if you're behind a firewall or proxy",
                            "Try again in a few moments",
                        ],
                    ) from e

                # Handle httpx HTTP status errors
                if hasattr(e, "__class__") and e.__class__.__name__ == "HTTPStatusError":
                    # httpx.HTTPStatusError - extract status code
                    status_code = None
                    if hasattr(e, "response") and hasattr(e.response, "status_code"):
                        status_code = e.response.status_code

                    # Map specific status codes to SDK-level exceptions
                    if status_code == 429 or status_code == 503:
                        from flow.errors import APIError

                        raise APIError(
                            f"{operation} failed: {str(e)}",
                            status_code=status_code,
                            response_body=(
                                getattr(e.response, "text", None)
                                if hasattr(e, "response")
                                else None
                            ),
                        ) from e

                # Log unexpected errors
                logger.error(f"{operation} failed with unexpected error: {e}", exc_info=True)
                raise FCPAPIError(f"{operation} failed: {str(e)}") from e

        return wrapper

    return decorator


def safe_get(data: dict, *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary values.

    Args:
        data: Dictionary to extract from
        keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Value at the key path or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def validate_response(response: Any, required_fields: list[str]) -> dict:
    """Validate API response has required fields.

    Args:
        response: API response to validate
        required_fields: List of required field names

    Returns:
        Response as dict

    Raises:
        FCPAPIError: If response is invalid
    """
    if not isinstance(response, dict):
        raise FCPAPIError(f"Invalid response type: expected dict, got {type(response)}")

    missing_fields = [field for field in required_fields if field not in response]
    if missing_fields:
        raise FCPAPIError(f"Missing required fields in response: {', '.join(missing_fields)}")

    return response
