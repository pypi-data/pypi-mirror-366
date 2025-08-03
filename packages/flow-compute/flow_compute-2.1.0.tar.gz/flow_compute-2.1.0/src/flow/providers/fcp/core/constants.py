"""FCP-specific constants and configuration values.

This module centralizes all FCP-specific constants to improve maintainability
and make it easier to update provider-specific values.

All API constants, enums, and validated values from the FCP OpenAPI specification
are defined here to avoid hardcoding throughout the codebase.
"""

import os
from enum import Enum
from typing import Any, Dict, List

# ==================== Regions ====================
# Verified from FCP API /v2/spot/availability endpoint
VALID_REGIONS: List[str] = [
    "eu-central1-a",
    "eu-central1-b",
    "us-central1-a",
    "us-central1-b",
]

# Startup Script Limits
# FCP has a 10,000 character limit for uncompressed startup scripts
# Source: https://docs.mlfoundry.com/compute-and-storage/startup-scripts
STARTUP_SCRIPT_MAX_SIZE = 10 * 1000  # 10,000 characters

# Log Locations
# FCP expects logs at specific locations for compatibility
FCP_LOG_DIR = os.getenv("FCP_LOG_DIR", "/var/log/foundry")
FCP_STARTUP_LOG = f"{FCP_LOG_DIR}/startup_script.log"

# Flow's internal log locations
FLOW_LOG_DIR = os.getenv("FLOW_LOG_DIR", "/var/log/flow")
FLOW_LEGACY_LOG_DIR = os.getenv("FLOW_LEGACY_LOG_DIR", "/var/log/fcp")  # For backward compatibility

# ==================== Storage ====================
# Disk interface types from FCP API
# Note: UI shows "File share" but API expects "File"
DISK_INTERFACE_BLOCK = "Block"
DISK_INTERFACE_FILE = "File"

VALID_DISK_INTERFACES = [DISK_INTERFACE_BLOCK, DISK_INTERFACE_FILE]


# ==================== Instance Status ====================
class InstanceStatus(str, Enum):
    """Instance lifecycle statuses from API."""

    PENDING = "STATUS_PENDING"
    NEW = "STATUS_NEW"
    CONFIRMED = "STATUS_CONFIRMED"
    SCHEDULED = "STATUS_SCHEDULED"
    INITIALIZING = "STATUS_INITIALIZING"
    STARTING = "STATUS_STARTING"
    RUNNING = "STATUS_RUNNING"
    STOPPING = "STATUS_STOPPING"
    STOPPED = "STATUS_STOPPED"
    TERMINATED = "STATUS_TERMINATED"
    RELOCATING = "STATUS_RELOCATING"
    PREEMPTING = "STATUS_PREEMPTING"
    PREEMPTED = "STATUS_PREEMPTED"
    REPLACED = "STATUS_REPLACED"


# ==================== Bid Status ====================
class BidStatus(str, Enum):
    """Bid/Task statuses from API."""

    OPEN = "Open"
    ALLOCATED = "Allocated"
    PREEMPTING = "Preempting"
    TERMINATED = "Terminated"
    PAUSED = "Paused"
    REPLACED = "Replaced"


# ==================== Order Types ====================
class OrderType(str, Enum):
    """Types of orders in FCP."""

    BID = "Bid"
    RESERVATION = "Reservation"


# ==================== Sort Options ====================
class SortDirection(str, Enum):
    """Sort directions for API queries."""

    ASC = "asc"
    DESC = "desc"


# Instance Type Mappings
# Verified from FCP API /v2/instance-types endpoint (2025-07-20)
INSTANCE_TYPE_MAPPINGS = {
    # A100 mappings
    "a100": "it_MsIRhxj3ccyVWGfP",  # Default to 1x
    "1xa100": "it_MsIRhxj3ccyVWGfP",
    "2xa100": "it_5M6aGxGovNeX5ltT",
    "4xa100": "it_fK7Cx6TVhOK5ZfXT",
    "8xa100": "it_J7OyNf9idfImLIFo",
    # FCP format also supported
    "a100-80gb.sxm.1x": "it_MsIRhxj3ccyVWGfP",
    "a100-80gb.sxm.2x": "it_5M6aGxGovNeX5ltT",
    "a100-80gb.sxm.4x": "it_fK7Cx6TVhOK5ZfXT",
    "a100-80gb.sxm.8x": "it_J7OyNf9idfImLIFo",
    # H100 mappings
    "h100": "it_5ECSoHQjLBzrp5YM",  # Default to 8x
    "8xh100": "it_5ECSoHQjLBzrp5YM",
    "h100-80gb.sxm.8x": "it_5ECSoHQjLBzrp5YM",
    # Note: it_XqgKWbhZ5gznAYsG also maps to h100-80gb.sxm.8x in API
}

# Reverse mapping for display purposes
# Verified from FCP API /v2/instance-types endpoint (2025-07-20)
INSTANCE_TYPE_NAMES = {
    "it_MsIRhxj3ccyVWGfP": "a100-80gb.sxm.1x",
    "it_5M6aGxGovNeX5ltT": "a100-80gb.sxm.2x",
    "it_fK7Cx6TVhOK5ZfXT": "a100-80gb.sxm.4x",
    "it_J7OyNf9idfImLIFo": "a100-80gb.sxm.8x",
    "it_5ECSoHQjLBzrp5YM": "h100-80gb.sxm.8x",
    "it_XqgKWbhZ5gznAYsG": "h100-80gb.sxm.8x",  # Another H100 variant
}

# API Endpoints
import os

FCP_API_BASE_URL = os.getenv("FCP_API_URL", "https://api.mlfoundry.com")
FCP_API_VERSION = "v2"
FCP_WEB_BASE_URL = os.getenv("FCP_WEB_URL", "https://app.mlfoundry.com")
FCP_DOCS_URL = os.getenv("FCP_DOCS_URL", "https://docs.mlfoundry.com")
FCP_STATUS_URL = os.getenv("FCP_STATUS_URL", "https://status.mlfoundry.com")

# Resource Limits
MAX_VOLUMES_PER_INSTANCE = 20  # AWS limit that FCP inherits
MAX_INSTANCES_PER_TASK = 256
MAX_VOLUME_SIZE_GB = 16384  # 16TB

# Timeouts
DEFAULT_HTTP_TIMEOUT = 30  # seconds
VOLUME_DELETE_TIMEOUT = 120  # seconds, volume deletion can be slow

# ==================== Instance Provisioning Times ====================
# FCP instances can take significant time to provision and become ready
# These constants centralize timing assumptions for better maintainability

# Time for instance to get allocated and receive an IP address
INSTANCE_IP_WAIT_SECONDS = 300  # 5 minutes max to get IP
INSTANCE_IP_CHECK_INTERVAL = 5  # Check every 5 seconds

# Time for SSH to become available after IP is assigned
SSH_READY_WAIT_SECONDS = 600  # 10 minutes max for SSH readiness
SSH_CHECK_INTERVAL = 2  # Check every 2 seconds

# Total expected provisioning time (for user messages)
EXPECTED_PROVISION_MINUTES = 20  # "FCP instances can take up to 20 minutes"

# Quick SSH retry for commands (logs, etc)
SSH_QUICK_RETRY_ATTEMPTS = 5
SSH_QUICK_RETRY_MAX_SECONDS = 30  # 30 seconds total for quick retries

# User Cache
USER_CACHE_TTL = 3600  # 1 hour TTL for user information cache

# SSH Configuration
DEFAULT_SSH_USER = os.getenv("FCP_SSH_USER", "ubuntu")
DEFAULT_SSH_PORT = int(os.getenv("FCP_SSH_PORT", "22"))

# Volume Configuration
VOLUME_ID_PREFIX = "vol_"

# Status Mappings
# Map FCP status strings to TaskStatus enum values
STATUS_MAPPINGS = {
    "pending": "PENDING",
    "open": "PENDING",  # FCP uses "Open" for pending bids
    "provisioning": "PENDING",  # Still waiting for allocation
    "paused": "PAUSED",  # Instance paused - no billing, no SSH access
    "preempting": "PREEMPTING",  # FCP spot instance will be terminated soon
    "allocated": "RUNNING",  # FCP uses "Allocated" for running instances
    "running": "RUNNING",
    "completed": "COMPLETED",
    "failed": "FAILED",
    "cancelled": "CANCELLED",
    "terminated": "CANCELLED",
    "replaced": "CANCELLED",  # Bid was replaced by another bid
}

# Supported Regions
# DEPRECATED: Use VALID_REGIONS instead
# This list was incorrect and used a different naming convention
SUPPORTED_REGIONS = VALID_REGIONS  # Use the same list for compatibility

# Default Region
DEFAULT_REGION = os.getenv("FCP_DEFAULT_REGION", "us-central1-b")

# ==================== Instance Types ====================
# Note: These should be fetched dynamically from /v2/instance-types
# This is just for reference/examples
EXAMPLE_INSTANCE_TYPES = [
    "h100.80gb.sxm",
    "a100.80gb.sxm",
    "a40.48gb.pcie",
]

# ==================== GPU Instance Detection ====================
# Patterns for detecting GPU instances based on instance type names
# Used for determining when to add --gpus flag and install nvidia-container-toolkit
GPU_INSTANCE_PATTERNS = [
    "gpu",  # Generic GPU prefix
    "a100",  # NVIDIA A100
    "a10",  # NVIDIA A10
    "h100",  # NVIDIA H100
    "v100",  # NVIDIA V100
    "t4",  # NVIDIA T4
    "l4",  # NVIDIA L4
    "a40",  # NVIDIA A40
    "p100",  # NVIDIA P100
    "k80",  # NVIDIA K80
    "m60",  # NVIDIA M60
    "rtx",  # RTX series
    "tesla",  # Tesla series
    "nvidia",  # Explicit nvidia naming
]

# ==================== API Defaults ====================
DEFAULT_DISK_INTERFACE = DISK_INTERFACE_BLOCK

# ==================== Validation Messages ====================
# Centralized validation help messages
VALIDATION_MESSAGES = {
    "region": {
        "help": "Valid regions",
        "examples": VALID_REGIONS,
        "note": "Additional regions may be available. Check FCP documentation.",
    },
    "disk_interface": {
        "help": "Valid disk interfaces",
        "examples": [
            f"{DISK_INTERFACE_BLOCK} (high-performance block storage)",
            f"{DISK_INTERFACE_FILE} (shared file storage)",
        ],
    },
    "instance_type": {
        "help": "Example instance types",
        "examples": [
            "a100-80gb.sxm.4x (4x A100 GPUs)",
            "h100-80gb.sxm.8x (8x H100 GPUs)",
            "t4-16gb.pcie.1x (1x T4 GPU)",
        ],
        "note": "Run 'flow instances' to see all available types",
    },
}


def get_validation_help(field: str) -> Dict[str, Any]:
    """Get validation help message for a field.

    Args:
        field: Field name to get help for

    Returns:
        Dictionary with help, examples, and optional note
    """
    return VALIDATION_MESSAGES.get(field, {})


def format_validation_help(field: str) -> List[str]:
    """Format validation help as list of strings for error messages.

    Args:
        field: Field name to format help for

    Returns:
        List of formatted help strings
    """
    help_info = get_validation_help(field)
    if not help_info:
        return []

    lines = []

    if help_info.get("help"):
        lines.append(f"{help_info['help']}:")

    for example in help_info.get("examples", []):
        lines.append(f"  - {example}")

    if help_info.get("note"):
        if lines:
            lines.append("")
        lines.append(help_info["note"])

    return lines
