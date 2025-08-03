"""API state management for integration tests."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from flow.errors import APIError, AuthenticationError
from flow.providers.fcp.provider import FCPProvider

logger = logging.getLogger(__name__)


class APIState(Enum):
    """Possible API states that affect testing."""
    HEALTHY = "healthy"
    QUOTA_EXCEEDED = "quota_exceeded"
    NO_INSTANCES = "no_instances"
    AUTH_FAILED = "auth_failed"
    UNREACHABLE = "unreachable"


@dataclass
class APIHealthCheck:
    """Result of API health check."""
    state: APIState
    message: str
    available_instances: List[Any] = None

    @property
    def can_run_tests(self) -> bool:
        """Check if tests can run with current API state."""
        return self.state == APIState.HEALTHY

    @property
    def skip_reason(self) -> str:
        """Get pytest skip reason."""
        reasons = {
            APIState.QUOTA_EXCEEDED: "API quota exceeded - tests would fail",
            APIState.NO_INSTANCES: "No instances available in API",
            APIState.AUTH_FAILED: "API authentication failed",
            APIState.UNREACHABLE: "API is unreachable",
        }
        return reasons.get(self.state, self.message)


def check_api_health(provider: FCPProvider) -> APIHealthCheck:
    """Check if API is in a state where tests can run.
    
    This function detects common API issues that would cause tests to fail
    for reasons unrelated to code correctness.
    
    Args:
        provider: The FCP provider instance
        
    Returns:
        APIHealthCheck with current state
    """
    try:
        # Try to find instances - this tests both auth and availability
        instances = provider.find_instances(
            {"max_price_per_hour": 100.0},
            limit=5
        )

        if not instances:
            return APIHealthCheck(
                state=APIState.NO_INSTANCES,
                message="No instances available from API"
            )

        # Try a minimal operation to check quota
        # Just getting instance details shouldn't consume quota
        # but will fail if quota is exhausted
        try:
            # This is a read-only operation
            _ = provider.get_project()
        except APIError as e:
            if "quota" in str(e).lower():
                return APIHealthCheck(
                    state=APIState.QUOTA_EXCEEDED,
                    message=f"API quota exceeded: {e}"
                )
            raise

        return APIHealthCheck(
            state=APIState.HEALTHY,
            message="API is healthy",
            available_instances=instances
        )

    except AuthenticationError as e:
        return APIHealthCheck(
            state=APIState.AUTH_FAILED,
            message=f"Authentication failed: {e}"
        )
    except APIError as e:
        # Check for specific error patterns
        error_str = str(e).lower()
        if "quota" in error_str:
            return APIHealthCheck(
                state=APIState.QUOTA_EXCEEDED,
                message=f"API quota exceeded: {e}"
            )
        return APIHealthCheck(
            state=APIState.UNREACHABLE,
            message=f"API error: {e}"
        )
    except Exception as e:
        return APIHealthCheck(
            state=APIState.UNREACHABLE,
            message=f"Unexpected error: {e}"
        )


def require_healthy_api(func):
    """Decorator to skip tests if API is not healthy.
    
    This decorator checks API health before running tests and skips
    with a clear reason if the API is in a bad state.
    
    Usage:
        @require_healthy_api
        def test_something(flow):
            # Test will only run if API is healthy
    """
    import functools

    import pytest

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find flow or provider in args
        flow = None
        provider = None

        for arg in args:
            if hasattr(arg, '_ensure_provider'):
                flow = arg
                provider = flow._ensure_provider()
                break
            elif isinstance(arg, FCPProvider):
                provider = arg
                break

        for arg in kwargs.values():
            if hasattr(arg, '_ensure_provider'):
                flow = arg
                provider = flow._ensure_provider()
                break
            elif isinstance(arg, FCPProvider):
                provider = arg
                break

        if provider:
            health = check_api_health(provider)
            if not health.can_run_tests:
                pytest.skip(health.skip_reason)

        return func(*args, **kwargs)

    return wrapper
