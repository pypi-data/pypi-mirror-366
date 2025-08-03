"""Core FCP provider components - models, constants, and errors.

This package contains the foundational elements of the FCP provider:
- Domain models (FCPBid, FCPInstance, FCPVolume, Auction)
- Constants and configuration values
- FCP-specific error types
"""

from .constants import (
    DEFAULT_REGION,
    DEFAULT_SSH_PORT,
    DEFAULT_SSH_USER,
    DISK_INTERFACE_BLOCK,
    DISK_INTERFACE_FILE,
    FCP_LOG_DIR,
    FCP_STARTUP_LOG,
    FLOW_LEGACY_LOG_DIR,
    FLOW_LOG_DIR,
    MAX_INSTANCES_PER_TASK,
    MAX_VOLUME_SIZE_GB,
    STARTUP_SCRIPT_MAX_SIZE,
    STATUS_MAPPINGS,
    SUPPORTED_REGIONS,
    USER_CACHE_TTL,
    VALID_DISK_INTERFACES,
    VALID_REGIONS,
    VOLUME_DELETE_TIMEOUT,
    VOLUME_ID_PREFIX,
)
from .errors import (
    FCPAPIError,
    FCPAuthenticationError,
    FCPBidError,
    FCPError,
    FCPInstanceError,
    FCPQuotaExceededError,
    FCPResourceNotFoundError,
    FCPTimeoutError,
    FCPValidationError,
    FCPVolumeError,
)
from .models import Auction, FCPBid, FCPInstance, FCPVolume

__all__ = [
    # Constants
    "VALID_REGIONS",
    "STARTUP_SCRIPT_MAX_SIZE",
    "DISK_INTERFACE_BLOCK",
    "DISK_INTERFACE_FILE",
    "VALID_DISK_INTERFACES",
    "DEFAULT_REGION",
    "DEFAULT_SSH_PORT",
    "DEFAULT_SSH_USER",
    "FCP_LOG_DIR",
    "FCP_STARTUP_LOG",
    "FLOW_LEGACY_LOG_DIR",
    "FLOW_LOG_DIR",
    "MAX_INSTANCES_PER_TASK",
    "MAX_VOLUME_SIZE_GB",
    "STATUS_MAPPINGS",
    "SUPPORTED_REGIONS",
    "USER_CACHE_TTL",
    "VOLUME_DELETE_TIMEOUT",
    "VOLUME_ID_PREFIX",
    # Errors
    "FCPError",
    "FCPAPIError",
    "FCPAuthenticationError",
    "FCPResourceNotFoundError",
    "FCPQuotaExceededError",
    "FCPValidationError",
    "FCPTimeoutError",
    "FCPInstanceError",
    "FCPBidError",
    "FCPVolumeError",
    # Models
    "FCPBid",
    "FCPInstance",
    "FCPVolume",
    "Auction",
]
