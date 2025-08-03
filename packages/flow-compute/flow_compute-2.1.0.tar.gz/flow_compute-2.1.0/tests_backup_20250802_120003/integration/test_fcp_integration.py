"""Integration tests for FCP provider against real API.

These tests require FCP_TEST_API_KEY to be set and will make real API calls.
They test the actual integration between our code and the FCP API.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

logger = logging.getLogger(__name__)

from flow.api.models import TaskStatus
from flow.errors import ResourceNotFoundError
from flow.providers.fcp.core.errors import FCPResourceNotFoundError
from tests.testing import (
    MetricsCollector,
    TaskConfigBuilder,
    create_test_provider,
    isolation_context,
    submit_test_task,
    wait_for_task_status,
)


@pytest.mark.integration
class TestFCPRealIntegration:
    """Test real integration with FCP API.
    
    These tests:
    - Use real API credentials
    - Make real API calls
    - Allocate real resources (in sandbox)
    - Verify actual behavior
    """

    @pytest.fixture(scope="class")
    def provider(self):
        """Create real provider for integration tests."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
        return create_test_provider()

    @pytest.fixture
    def metrics(self):
        """Track metrics during tests."""
        return MetricsCollector()

    def test_find_available_instances(self, provider, metrics):
        """Test finding real available instances."""
        # Test that we can find ANY available instances
        with metrics.measure("find_instances"):
            instances = provider.find_instances({
                "max_price_per_hour": 100.0
            }, limit=5)

        # Should find some instances
        assert len(instances) > 0

        # Verify instance data structure is correct
        for instance in instances:
            # Verify required fields exist and are valid
            assert instance.allocation_id  # Should have allocation ID
            assert instance.instance_type  # Should have instance type (even if opaque)
            assert isinstance(instance.price_per_hour, (int, float))
            assert instance.price_per_hour > 0
            assert instance.region  # Should have region

        # Verify all instances have valid prices
        prices = [i.price_per_hour for i in instances]
        assert all(p > 0 for p in prices), "All prices should be positive"

    def test_complete_task_lifecycle(self, provider, metrics):
        """Test complete task lifecycle with real infrastructure."""
        with isolation_context(provider) as context:
            # Find an available instance first
            instances = provider.find_instances({"max_price_per_hour": 50.0}, limit=1)
            if not instances:
                pytest.skip("No instances available for testing")

            # Use the discovered instance type
            instance_type = instances[0].instance_type

            # Submit real task
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-lifecycle-test")
                .with_instance_type(instance_type)
                .with_command("echo 'Hello from integration test'; sleep 5")
                .with_max_price(50.0)
                .with_upload_code(False)
                .build())

            with metrics.measure("submit_task"):
                task = submit_test_task(provider, config)

            # Track task ID for cleanup
            context["created_resources"].append(("task", task.task_id))

            # Verify initial state
            assert task.task_id
            assert task.status in [TaskStatus.PENDING, TaskStatus.QUEUED]

            # Wait for task to start
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.RUNNING, timeout=60
            )

            # Get updated task info
            running_task = provider.get_task(task.task_id)
            assert running_task.status == TaskStatus.RUNNING
            assert running_task.started_at is not None
            assert running_task.instance_id is not None

            # Get logs while running
            logs = provider.get_logs(task.task_id)
            assert "Hello from integration test" in logs

            # Wait for completion
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.COMPLETED, timeout=120
            )

            # Verify final state
            completed_task = provider.get_task(task.task_id)
            assert completed_task.status == TaskStatus.COMPLETED
            assert completed_task.completed_at is not None
            assert completed_task.total_cost is not None

        # Report metrics
        print(f"Metrics: {metrics.report()}")

    def test_task_cancellation(self, provider):
        """Test cancelling a real running task."""
        with isolation_context(provider) as context:
            # Find an available instance first
            instances = provider.find_instances({"max_price_per_hour": 50.0}, limit=1)
            if not instances:
                pytest.skip("No instances available for testing")

            # Submit long-running task
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-cancel-test")
                .with_instance_type(instances[0].instance_type)
                .with_command("sleep 300")  # 5 minutes
                .with_upload_code(False)
                .build())

            task = submit_test_task(provider, config)
            context["created_resources"].append(("task", task.task_id))

            # Wait for it to start
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.RUNNING, timeout=60
            )

            # Cancel it
            cancelled = provider.cancel_task(task.task_id)
            assert cancelled is True

            # Verify it's cancelled
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.CANCELLED, timeout=30
            )

    def test_concurrent_task_submission(self, provider):
        """Test submitting multiple tasks concurrently."""
        with isolation_context(provider) as context:
            # Find available instances first
            instances = provider.find_instances({"max_price_per_hour": 50.0}, limit=5)
            if len(instances) < 3:
                pytest.skip("Not enough instances available for concurrent test")

            num_tasks = 3
            configs = [
                TaskConfigBuilder()
                .with_name(f"{context['namespace']}-concurrent-{i}")
                .with_command(f"echo 'Task {i}'; sleep 2")
                .with_instance_type(instances[i % len(instances)].instance_type)
                .with_max_price(50.0)
                .with_upload_code(False)
                .build()
                for i in range(num_tasks)
            ]

            # Submit concurrently using ThreadPoolExecutor
            def submit_wrapper(config):
                try:
                    return submit_test_task(provider, config)
                except Exception as e:
                    return e

            # Use ThreadPoolExecutor for concurrent submission
            with ThreadPoolExecutor(max_workers=num_tasks) as executor:
                futures = [executor.submit(submit_wrapper, config) for config in configs]
                tasks = [f.result() for f in as_completed(futures)]

            # Check results
            successful_tasks = []
            for i, result in enumerate(tasks):
                if isinstance(result, Exception):
                    logger.warning(f"Task {i} failed: {result}")
                else:
                    successful_tasks.append(result)
                    context["created_resources"].append(("task", result.task_id))

            # At least one should succeed
            assert len(successful_tasks) > 0, "All concurrent submissions failed"
            tasks = successful_tasks

            # All should succeed
            assert len(tasks) == num_tasks

            # All should have unique IDs
            task_ids = [t.task_id for t in tasks]
            assert len(set(task_ids)) == num_tasks

    def test_invalid_instance_type_error(self, provider):
        """Test that invalid instance types are rejected."""
        # Import the correct error type
        from flow.providers.fcp.core.errors import FCPAPIError

        # This should fail when trying to find instances
        with pytest.raises(FCPAPIError) as exc_info:
            provider.find_instances({
                "instance_type": "invalid-gpu-type"
            }, limit=1)

        # Verify the error message is helpful
        error_msg = str(exc_info.value)
        assert "Unknown instance type: invalid-gpu-type" in error_msg
        assert "Available:" in error_msg
        assert "a100" in error_msg  # Should list valid options

    def test_nonexistent_task_error(self, provider):
        """Test that querying nonexistent tasks raises proper error."""
        with pytest.raises(FCPResourceNotFoundError):
            provider.get_task("task-does-not-exist")

    def test_gpu_instance_allocation(self, provider):
        """Test submitting a task to a real GPU instance."""
        # Find any available instance
        instances = provider.find_instances({
            "max_price_per_hour": 50.0
        }, limit=1)

        if not instances:
            pytest.skip("No instances available in test environment")

        with isolation_context(provider) as context:
            # Use the instance type that's actually available
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-gpu-test")
                .with_instance_type(instances[0].instance_type)
                .with_region(instances[0].region)
                .with_command("echo 'Test task submitted'")
                .with_max_price(50.0)
                .with_upload_code(False)
                .build())

            # Submit task
            task = provider.submit_task(
                instance_id=instances[0].allocation_id,
                config=config
            )
            context["created_resources"].append(("task", task.task_id))

            # Verify task was created
            assert task.task_id
            assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

            # Verify instance resolution worked
            print(f"Successfully submitted task {task.task_id} to {instances[0].instance_type}")


@pytest.mark.integration
class TestFCPStorageIntegration:
    """Test storage operations against real API."""

    @pytest.fixture(scope="class")
    def provider(self):
        """Create real provider for integration tests."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
        return create_test_provider()

    def test_volume_lifecycle(self, provider):
        """Test creating, listing, and deleting volumes."""
        with isolation_context(provider) as context:
            # Create volume
            volume = provider.create_volume(
                name=f"{context['namespace']}-test-volume",
                size_gb=10
            )
            context["created_resources"].append(("volume", volume.volume_id))

            # Verify creation
            assert volume.volume_id
            assert volume.size_gb == 10
            assert volume.status == "available"

            # List volumes
            volumes = provider.list_volumes()
            volume_ids = [v.volume_id for v in volumes]
            assert volume.volume_id in volume_ids

            # Delete volume
            deleted = provider.delete_volume(volume.volume_id)
            assert deleted is True

            # Verify deletion
            with pytest.raises(ResourceNotFoundError):
                provider.get_volume(volume.volume_id)
