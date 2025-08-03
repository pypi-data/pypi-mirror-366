"""Flow SDK - GPU compute made simple."""

# Public API imports
from flow.api.client import Flow
from flow.api.decorators import FlowApp, app
from flow.api.invoke import invoke
from flow.api.models import Task, TaskConfig, TaskStatus, Volume, VolumeSpec, Retries
from flow.api.secrets import Secret

# Public errors and constants
from flow.errors import (
    APIError,
    AuthenticationError,
    ConfigParserError,
    FlowError,
    FlowOperationError,
    InsufficientBidPriceError,
    NetworkError,
    ProviderError,
    QuotaExceededError,
    ResourceNotAvailableError,
    ResourceNotFoundError,
    TaskExecutionError,
    TaskNotFoundError,
    TimeoutError,
    ValidationAPIError,
    ValidationError,
    VolumeError,
)
from flow.providers.fcp.core.constants import DEFAULT_REGION

# Version
try:
    from importlib.metadata import version

    __version__ = version("flow-sdk")
except Exception:
    __version__ = "0.0.0+unknown"

__all__ = [
    # Main API
    "Flow",
    "FlowApp",
    "invoke",
    "app",
    # Models
    "TaskConfig",
    "Task",
    "Volume",
    "VolumeSpec",
    "TaskStatus",
    "Secret",
    "Retries",
    # Errors
    "FlowError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "TaskNotFoundError",
    "ValidationError",
    "APIError",
    "ValidationAPIError",
    "InsufficientBidPriceError",
    "NetworkError",
    "TimeoutError",
    "ProviderError",
    "ConfigParserError",
    "ResourceNotAvailableError",
    "QuotaExceededError",
    "VolumeError",
    "TaskExecutionError",
    "FlowOperationError",
    # Constants
    "DEFAULT_REGION",
]
