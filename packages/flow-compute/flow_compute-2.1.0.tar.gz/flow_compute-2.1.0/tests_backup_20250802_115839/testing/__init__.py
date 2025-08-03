"""Test infrastructure for Flow SDK.

This package provides builders and utilities for writing
maintainable tests that follow SOLID principles.

Core philosophy: Test real systems, not fakes.
"""

from .api_state import (
    APIHealthCheck,
    APIState,
    check_api_health,
    require_healthy_api,
)
from .base import IntegrationTest
from .builders import (
    InstanceBuilder,
    TaskBuilder,
    TaskConfigBuilder,
    VolumeBuilder,
)
from .providers import (
    MetricsCollector,
    create_test_provider,
    isolation_context,
    wait_for_task_status,
)
from .task_helpers import (
    discover_available_instance_type,
    skip_if_no_instances,
    submit_test_task,
)

__all__ = [
    # Builders
    "TaskConfigBuilder",
    "VolumeBuilder",
    "InstanceBuilder",
    "TaskBuilder",
    # Provider utilities
    "create_test_provider",
    "isolation_context",
    "wait_for_task_status",
    "MetricsCollector",
    # Task helpers
    "submit_test_task",
    "discover_available_instance_type",
    "skip_if_no_instances",
    # API state management
    "APIState",
    "APIHealthCheck",
    "check_api_health",
    "require_healthy_api",
    # Base classes
    "IntegrationTest",
]
