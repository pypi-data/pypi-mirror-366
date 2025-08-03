"""Test utilities for working with real providers.

Following the philosophy: test real systems, not fakes.
"""

import os
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Optional

from flow._internal.config import Config
from flow.providers.fcp.provider import FCPProvider


def create_test_provider(
    api_key: Optional[str] = None,
    project_suffix: bool = False
) -> FCPProvider:
    """Create real FCP provider configured for testing.
    
    Uses sandbox environment and test credentials.
    Automatically cleans up resources after tests.
    
    Args:
        api_key: Override test API key
        project_suffix: Add unique suffix to project name for isolation
    
    Returns:
        Real FCPProvider instance configured for testing
    """
    # Get test credentials from environment
    test_api_key = api_key or os.environ.get("FCP_TEST_API_KEY")
    if not test_api_key:
        raise ValueError(
            "FCP_TEST_API_KEY environment variable required for testing. "
            "Set up test credentials at https://console.mlfoundry.com/test-mode"
        )

    # Use real API endpoint
    test_api_url = os.environ.get(
        "FCP_TEST_API_URL",
        "https://api.mlfoundry.com"
    )

    # Use available project
    base_project = os.environ.get("FCP_TEST_PROJECT", "test")
    if project_suffix:
        project = f"{base_project}-{uuid.uuid4().hex[:8]}"
    else:
        project = base_project

    # Create config for test provider
    config = Config(
        provider="fcp",
        auth_token=test_api_key,
        provider_config={
            "api_url": test_api_url,
            "project": project,
            "region": os.environ.get("FCP_TEST_REGION", "us-east-1"),
            "cleanup_on_exit": True,  # Auto cleanup test resources
            "test_mode": True  # Enable test mode features
        }
    )

    return FCPProvider.from_config(config)


@contextmanager
def isolation_context(provider: FCPProvider, namespace: str = None):
    """Run tests in isolated namespace with automatic cleanup.
    
    Args:
        provider: The provider instance
        namespace: Optional namespace prefix for resources
        
    Yields:
        Dict with test context including namespace
    """
    if namespace is None:
        namespace = f"test-{uuid.uuid4().hex[:8]}"

    context = {
        "namespace": namespace,
        "created_resources": [],
        "start_time": time.time()
    }

    try:
        yield context
    finally:
        # Cleanup all resources created during test
        cleanup_test_resources(provider, context)


def cleanup_test_resources(provider: FCPProvider, context: Dict[str, Any]):
    """Clean up all resources created during test.
    
    Args:
        provider: The provider instance
        context: Test context with resource tracking
    """
    errors = []

    # Cancel any running tasks
    try:
        tasks = provider.list_tasks()
        namespace = context["namespace"]
        for task in tasks:
            # Only clean up tasks from this test run
            if task.name and task.name.startswith(namespace):
                if task.status not in ["COMPLETED", "FAILED", "CANCELLED"]:
                    try:
                        provider.cancel_task(task.task_id)
                    except Exception as e:
                        errors.append(f"Failed to cancel task {task.task_id}: {e}")
    except Exception as e:
        errors.append(f"Failed to list tasks: {e}")

    # Delete test volumes
    try:
        volumes = provider.list_volumes()
        namespace = context["namespace"]
        for volume in volumes:
            # Only clean up volumes from this test run
            if volume.name and volume.name.startswith(namespace):
                try:
                    provider.delete_volume(volume.volume_id)
                except Exception as e:
                    errors.append(f"Failed to delete volume {volume.volume_id}: {e}")
    except Exception as e:
        errors.append(f"Failed to list volumes: {e}")

    if errors:
        print(f"Cleanup errors: {errors}")


def wait_for_task_status(
    provider: FCPProvider,
    task_id: str,
    expected_status: str,
    timeout: int = 60,
    poll_interval: float = 1.0
) -> bool:
    """Wait for task to reach expected status.
    
    Args:
        provider: The provider instance
        task_id: Task ID to monitor
        expected_status: Status to wait for
        timeout: Maximum time to wait in seconds
        poll_interval: Time between status checks
        
    Returns:
        True if status reached, False if timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            task = provider.get_task(task_id)
            if task.status == expected_status:
                return True

            # Check for terminal states
            if task.status in ["FAILED", "CANCELLED"] and expected_status not in ["FAILED", "CANCELLED"]:
                return False

        except Exception:
            # Task might not exist yet
            pass

        time.sleep(poll_interval)

    return False


class MetricsCollector:
    """Collect metrics during tests for performance analysis."""

    def __init__(self):
        self.api_calls = []
        self.durations = {}

    @contextmanager
    def measure(self, operation: str):
        """Measure duration of an operation."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            if operation not in self.durations:
                self.durations[operation] = []
            self.durations[operation].append(duration)

    def report(self) -> Dict[str, Any]:
        """Generate metrics report."""
        report = {}
        for op, durations in self.durations.items():
            report[op] = {
                "count": len(durations),
                "total": sum(durations),
                "mean": sum(durations) / len(durations) if durations else 0,
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0
            }
        return report
