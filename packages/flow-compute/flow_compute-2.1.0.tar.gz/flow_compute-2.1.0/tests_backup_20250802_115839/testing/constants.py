"""Centralized test constants following Google Python Style Guide.

This module contains all magic strings, numbers, and test constants used across
the test suite. By centralizing these values, we ensure consistency and make
the test suite more maintainable.

Design principles:
- No magic values inline in tests
- Clear, descriptive constant names
- Grouped by domain/feature area
- Immutable values only
"""

from datetime import timedelta
from typing import Dict, Final, List


class TestConstants:
    """Centralized test constants for the Flow SDK test suite.
    
    Following the principle of no magic values in tests, this class provides
    all test-related constants in a single, well-organized location.
    """
    
    # Test identification
    TEST_PREFIX: Final[str] = "test-"
    TEST_TASK_PREFIX: Final[str] = "test-task-"
    TEST_VOLUME_PREFIX: Final[str] = "test-volume-"
    TEST_BID_PREFIX: Final[str] = "bid-"
    TEST_INSTANCE_PREFIX: Final[str] = "i-"
    TEST_PROJECT_PREFIX: Final[str] = "proj-"
    TEST_USER_PREFIX: Final[str] = "user-"
    TEST_ALLOCATION_PREFIX: Final[str] = "alloc-"
    
    # Default test values
    DEFAULT_TEST_COMMAND: Final[List[str]] = ["echo", "test"]
    DEFAULT_TEST_SCRIPT: Final[str] = "echo 'test'"
    DEFAULT_INSTANCE_TYPE: Final[str] = "gpu.nvidia.h100"
    DEFAULT_GPU_TYPE: Final[str] = "h100-80gb"
    DEFAULT_REGION: Final[str] = "us-east-1"
    DEFAULT_MAX_PRICE: Final[float] = 10.0
    DEFAULT_VOLUME_SIZE_GB: Final[int] = 10
    DEFAULT_NUM_INSTANCES: Final[int] = 1
    
    # FCP-specific instance types
    FCP_INSTANCE_TYPES: Final[Dict[str, str]] = {
        "a100": "it_MsIRhxj3ccyVWGfP",
        "h100": "it_5ECSoHQjLBzrp5YM",
        "h100-pcie": "it_XqgKWbhZ5gznAYsG",
        "a10": "it_zMPE5XskFP9x2hTb",
        "v100": "it_8l9p3CnK5ZQM7xJd",
    }
    
    # Common test instance type (H100 PCIe)
    TEST_INSTANCE_TYPE_ID: Final[str] = "it_XqgKWbhZ5gznAYsG"
    TEST_INSTANCE_TYPE_NAME: Final[str] = "H100 80GB"
    
    # Status mappings for FCP
    FCP_STATUS_MAPPINGS: Final[Dict[str, str]] = {
        "pending": "PENDING",
        "provisioning": "PENDING",
        "allocated": "RUNNING",
        "running": "RUNNING",
        "completed": "COMPLETED",
        "failed": "FAILED",
        "terminated": "COMPLETED",
        "cancelled": "CANCELLED",
        "deactivated": "CANCELLED",
        "terminating": "CANCELLED",
    }
    
    # Test prices
    TEST_PRICE_LOW: Final[float] = 1.0
    TEST_PRICE_MEDIUM: Final[float] = 25.60
    TEST_PRICE_HIGH: Final[float] = 35.50
    TEST_PRICE_VERY_HIGH: Final[float] = 100.0
    TEST_PRICE_INVALID: Final[float] = 0.0
    
    # Test price strings
    TEST_PRICE_STRING_LOW: Final[str] = "$1.00"
    TEST_PRICE_STRING_MEDIUM: Final[str] = "$25.60"
    TEST_PRICE_STRING_HIGH: Final[str] = "$35.50"
    
    # Time-related constants
    TEST_DURATION_HOURS: Final[float] = 1.0
    TEST_STARTUP_DELAY_MINUTES: Final[int] = 2
    TEST_RUNTIME_PRECISION: Final[float] = 0.01  # Hours precision for assertions
    
    # Network timeouts (milliseconds)
    NETWORK_TIMEOUT_SHORT: Final[int] = 100
    NETWORK_TIMEOUT_MEDIUM: Final[int] = 1000
    NETWORK_TIMEOUT_LONG: Final[int] = 5000
    NETWORK_TIMEOUT_VERY_LONG: Final[int] = 30000
    
    # SSH-related constants
    SSH_DEFAULT_PORT: Final[int] = 22
    SSH_DEFAULT_USER: Final[str] = "root"
    SSH_CONNECTION_TIMEOUT: Final[int] = 10
    SSH_COMMAND_TIMEOUT: Final[int] = 30
    
    # Retry-related constants
    RETRY_MAX_ATTEMPTS: Final[int] = 3
    RETRY_INITIAL_DELAY: Final[float] = 0.1
    RETRY_MAX_DELAY: Final[float] = 5.0
    RETRY_BACKOFF_FACTOR: Final[float] = 2.0
    
    # Error messages
    ERROR_CONNECTION_REFUSED: Final[str] = "connection refused"
    ERROR_CONNECTION_TIMEOUT: Final[str] = "connection timed out"
    ERROR_NETWORK_UNREACHABLE: Final[str] = "network unreachable"
    ERROR_HOST_UNREACHABLE: Final[str] = "host unreachable"
    ERROR_DNS_FAILURE: Final[str] = "name resolution failed"
    
    # HTTP status codes
    HTTP_OK: Final[int] = 200
    HTTP_CREATED: Final[int] = 201
    HTTP_ACCEPTED: Final[int] = 202
    HTTP_NO_CONTENT: Final[int] = 204
    HTTP_BAD_REQUEST: Final[int] = 400
    HTTP_UNAUTHORIZED: Final[int] = 401
    HTTP_FORBIDDEN: Final[int] = 403
    HTTP_NOT_FOUND: Final[int] = 404
    HTTP_CONFLICT: Final[int] = 409
    HTTP_UNPROCESSABLE: Final[int] = 422
    HTTP_TOO_MANY_REQUESTS: Final[int] = 429
    HTTP_SERVER_ERROR: Final[int] = 500
    HTTP_BAD_GATEWAY: Final[int] = 502
    HTTP_SERVICE_UNAVAILABLE: Final[int] = 503
    HTTP_GATEWAY_TIMEOUT: Final[int] = 504
    
    # Volume constants
    VOLUME_MIN_SIZE_GB: Final[int] = 1
    VOLUME_MAX_SIZE_GB: Final[int] = 1000
    VOLUME_DELETE_TIMEOUT_SECONDS: Final[int] = 300
    
    # Task limits
    MAX_TASK_NAME_LENGTH: Final[int] = 128
    MAX_COMMAND_LENGTH: Final[int] = 32768
    MAX_ENV_VAR_COUNT: Final[int] = 100
    MAX_INSTANCES_PER_TASK: Final[int] = 8
    
    # File paths for testing
    TEST_WORK_DIR: Final[str] = "/tmp/flow-test"
    TEST_CODE_DIR: Final[str] = "/tmp/flow-test/code"
    TEST_LOG_DIR: Final[str] = "/tmp/flow-test/logs"
    
    # Mock responses
    MOCK_TASK_ID: Final[str] = "task-12345678"
    MOCK_INSTANCE_ID: Final[str] = "i-87654321"
    MOCK_VOLUME_ID: Final[str] = "vol-abcdef12"
    MOCK_PROJECT_ID: Final[str] = "proj-xyz789"
    MOCK_USER_ID: Final[str] = "user-abc123"
    
    # Test environment variables
    TEST_ENV_VARS: Final[Dict[str, str]] = {
        "TEST_MODE": "true",
        "DEBUG": "1",
        "LOG_LEVEL": "DEBUG",
    }
    
    # Assertion tolerances
    PRICE_TOLERANCE: Final[float] = 0.01
    TIME_TOLERANCE_SECONDS: Final[float] = 1.0
    
    @classmethod
    def get_test_task_name(cls, suffix: str = "") -> str:
        """Generate a test task name with optional suffix."""
        import uuid
        base = f"{cls.TEST_TASK_PREFIX}{uuid.uuid4().hex[:8]}"
        return f"{base}-{suffix}" if suffix else base
    
    @classmethod
    def get_test_volume_name(cls, suffix: str = "") -> str:
        """Generate a test volume name with optional suffix."""
        import uuid
        base = f"{cls.TEST_VOLUME_PREFIX}{uuid.uuid4().hex[:8]}"
        return f"{base}-{suffix}" if suffix else base
    
    @classmethod
    def get_mock_bid_id(cls) -> str:
        """Generate a mock bid ID."""
        import uuid
        return f"{cls.TEST_BID_PREFIX}{uuid.uuid4().hex[:8]}"
    
    @classmethod
    def get_mock_instance_id(cls) -> str:
        """Generate a mock instance ID."""
        import uuid
        return f"{cls.TEST_INSTANCE_PREFIX}{uuid.uuid4().hex[:8]}"


# Network simulation constants
class NetworkSimulation:
    """Constants for network failure simulation tests."""
    
    # Connection states
    CONNECTION_ACTIVE: Final[str] = "active"
    CONNECTION_DROPPED: Final[str] = "dropped"
    CONNECTION_SLOW: Final[str] = "slow"
    CONNECTION_FLAKY: Final[str] = "flaky"
    
    # Latency simulation (milliseconds)
    LATENCY_NORMAL: Final[int] = 50
    LATENCY_HIGH: Final[int] = 500
    LATENCY_VERY_HIGH: Final[int] = 2000
    LATENCY_TIMEOUT: Final[int] = 10000
    
    # Packet loss percentages
    PACKET_LOSS_NONE: Final[float] = 0.0
    PACKET_LOSS_LOW: Final[float] = 1.0
    PACKET_LOSS_MEDIUM: Final[float] = 5.0
    PACKET_LOSS_HIGH: Final[float] = 20.0
    PACKET_LOSS_SEVERE: Final[float] = 50.0
    
    # Bandwidth limits (bytes per second)
    BANDWIDTH_UNLIMITED: Final[int] = 0
    BANDWIDTH_SLOW: Final[int] = 10_000  # 10 KB/s
    BANDWIDTH_MEDIUM: Final[int] = 100_000  # 100 KB/s
    BANDWIDTH_FAST: Final[int] = 1_000_000  # 1 MB/s
    
    # Error injection probabilities
    ERROR_RATE_NONE: Final[float] = 0.0
    ERROR_RATE_LOW: Final[float] = 0.01
    ERROR_RATE_MEDIUM: Final[float] = 0.05
    ERROR_RATE_HIGH: Final[float] = 0.10
    
    # Retry scenarios
    RETRY_SCENARIO_SUCCESS: Final[str] = "immediate_success"
    RETRY_SCENARIO_EVENTUAL_SUCCESS: Final[str] = "eventual_success"
    RETRY_SCENARIO_PERMANENT_FAILURE: Final[str] = "permanent_failure"
    RETRY_SCENARIO_TIMEOUT: Final[str] = "timeout_failure"