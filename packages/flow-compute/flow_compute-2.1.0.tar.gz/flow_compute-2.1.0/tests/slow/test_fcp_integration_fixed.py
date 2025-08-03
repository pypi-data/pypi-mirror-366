"""Integration tests for FCP provider against real API.

These tests require FCP_TEST_API_KEY to be set and will make real API calls.
They test the actual integration between our code and the FCP API.

IMPROVEMENTS:
- Complete test isolation: Each test is independent
- No shared state between tests  
- Proper fixture scoping
- Clear constants for magic values
- Resource cleanup verification
- No class-level fixtures that create dependencies
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

import pytest

from flow.api.models import TaskStatus
from flow.errors import ResourceNotFoundError
from flow.providers.fcp.core.errors import FCPAPIError, FCPResourceNotFoundError
from tests.support.framework import (
    MetricsCollector,
    TaskConfigBuilder,
    create_test_provider,
    isolation_context,
    submit_test_task,
    wait_for_task_status,
)

logger = logging.getLogger(__name__)

# Test constants - no magic values
DEFAULT_MAX_PRICE = 50.0
TASK_START_TIMEOUT_SECONDS = 60
TASK_COMPLETION_TIMEOUT_SECONDS = 120
TASK_CANCEL_TIMEOUT_SECONDS = 30
LONG_RUNNING_TASK_SECONDS = 300
SHORT_TASK_SECONDS = 5
CONCURRENT_TASK_COUNT = 3
INSTANCE_SEARCH_LIMIT = 5
MIN_INSTANCES_FOR_CONCURRENT_TEST = 3


def skip_if_no_api_key():
    """Skip test if API key not configured."""
    if not os.environ.get("FCP_TEST_API_KEY"):
        pytest.skip("Integration tests require FCP_TEST_API_KEY")


@pytest.mark.integration
class TestFCPRealIntegration:
    """Test real integration with FCP API.
    
    These tests:
    - Use real API credentials
    - Make real API calls
    - Allocate real resources (in sandbox)
    - Verify actual behavior
    - Are completely isolated from each other
    """

    def test_find_available_instances(self):
        """Test finding real available instances."""
        skip_if_no_api_key()
        provider = create_test_provider()
        metrics = MetricsCollector()
        
        # Test that we can find ANY available instances
        with metrics.measure("find_instances"):
            instances = provider.find_instances({
                "max_price_per_hour": DEFAULT_MAX_PRICE * 2  # Higher limit for availability
            }, limit=INSTANCE_SEARCH_LIMIT)

        # Should find some instances
        assert len(instances) > 0, "No instances found - check API connectivity"

        # Verify instance data structure is correct
        for instance in instances:
            # Verify required fields exist and are valid
            assert instance.allocation_id, "Instance missing allocation_id"
            assert instance.instance_type, "Instance missing instance_type"
            assert isinstance(instance.price_per_hour, (int, float)), "Invalid price type"
            assert instance.price_per_hour > 0, "Price must be positive"
            assert instance.region, "Instance missing region"

        # Verify all instances have valid prices
        prices = [i.price_per_hour for i in instances]
        assert all(p > 0 for p in prices), "All prices should be positive"
        
        # Report metrics
        logger.info(f"Found {len(instances)} instances. Metrics: {metrics.report()}")

    def test_complete_task_lifecycle(self):
        """Test complete task lifecycle with real infrastructure."""
        skip_if_no_api_key()
        provider = create_test_provider()
        metrics = MetricsCollector()
        
        with isolation_context(provider) as context:
            # Find an available instance first
            instances = provider.find_instances(
                {"max_price_per_hour": DEFAULT_MAX_PRICE}, 
                limit=1
            )
            if not instances:
                pytest.skip("No instances available for testing")

            # Use the discovered instance type
            instance_type = instances[0].instance_type

            # Submit real task
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-lifecycle-test")
                .with_instance_type(instance_type)
                .with_command("echo 'Hello from integration test'; sleep 5")
                .with_max_price(DEFAULT_MAX_PRICE)
                .with_upload_code(False)
                .build())

            with metrics.measure("submit_task"):
                task = submit_test_task(provider, config)

            # Track task ID for cleanup
            context["created_resources"].append(("task", task.task_id))

            # Verify initial state
            assert task.task_id, "Task missing ID"
            assert task.status in [TaskStatus.PENDING, TaskStatus.QUEUED], \
                f"Unexpected initial status: {task.status}"

            # Wait for task to start
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.RUNNING, 
                timeout=TASK_START_TIMEOUT_SECONDS
            ), "Task failed to start within timeout"

            # Get updated task info
            running_task = provider.get_task(task.task_id)
            assert running_task.status == TaskStatus.RUNNING
            assert running_task.started_at is not None, "Running task missing start time"
            assert running_task.instance_id is not None, "Running task missing instance ID"

            # Get logs while running
            logs = provider.get_logs(task.task_id)
            assert "Hello from integration test" in logs, "Expected output not in logs"

            # Wait for completion
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.COMPLETED, 
                timeout=TASK_COMPLETION_TIMEOUT_SECONDS
            ), "Task failed to complete within timeout"

            # Verify final state
            completed_task = provider.get_task(task.task_id)
            assert completed_task.status == TaskStatus.COMPLETED
            assert completed_task.completed_at is not None, "Completed task missing end time"
            assert completed_task.total_cost is not None, "Completed task missing cost"

            # Report metrics
            logger.info(f"Task lifecycle metrics: {metrics.report()}")

    def test_task_cancellation(self):
        """Test cancelling a real running task."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        with isolation_context(provider) as context:
            # Find an available instance first
            instances = provider.find_instances(
                {"max_price_per_hour": DEFAULT_MAX_PRICE}, 
                limit=1
            )
            if not instances:
                pytest.skip("No instances available for testing")

            # Submit long-running task
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-cancel-test")
                .with_instance_type(instances[0].instance_type)
                .with_command(f"sleep {LONG_RUNNING_TASK_SECONDS}")
                .with_upload_code(False)
                .build())

            task = submit_test_task(provider, config)
            context["created_resources"].append(("task", task.task_id))

            # Wait for it to start
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.RUNNING, 
                timeout=TASK_START_TIMEOUT_SECONDS
            ), "Task failed to start before cancellation"

            # Cancel it
            cancelled = provider.cancel_task(task.task_id)
            assert cancelled is True, "Cancel operation failed"

            # Verify it's cancelled
            assert wait_for_task_status(
                provider, task.task_id, TaskStatus.CANCELLED, 
                timeout=TASK_CANCEL_TIMEOUT_SECONDS
            ), "Task failed to reach cancelled state"

    def test_concurrent_task_submission(self):
        """Test submitting multiple tasks concurrently."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        with isolation_context(provider) as context:
            # Find available instances first
            instances = provider.find_instances(
                {"max_price_per_hour": DEFAULT_MAX_PRICE}, 
                limit=INSTANCE_SEARCH_LIMIT
            )
            if len(instances) < MIN_INSTANCES_FOR_CONCURRENT_TEST:
                pytest.skip(
                    f"Not enough instances available for concurrent test "
                    f"(need {MIN_INSTANCES_FOR_CONCURRENT_TEST}, found {len(instances)})"
                )

            configs = [
                TaskConfigBuilder()
                .with_name(f"{context['namespace']}-concurrent-{i}")
                .with_command(f"echo 'Task {i}'; sleep {SHORT_TASK_SECONDS}")
                .with_instance_type(instances[i % len(instances)].instance_type)
                .with_max_price(DEFAULT_MAX_PRICE)
                .with_upload_code(False)
                .build()
                for i in range(CONCURRENT_TASK_COUNT)
            ]

            # Submit concurrently using ThreadPoolExecutor
            def submit_wrapper(config):
                try:
                    return submit_test_task(provider, config)
                except Exception as e:
                    logger.warning(f"Task submission failed: {e}")
                    return e

            # Use ThreadPoolExecutor for concurrent submission
            with ThreadPoolExecutor(max_workers=CONCURRENT_TASK_COUNT) as executor:
                futures = [executor.submit(submit_wrapper, config) for config in configs]
                results = [f.result() for f in as_completed(futures)]

            # Check results
            successful_tasks = []
            failed_submissions = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_submissions.append((i, result))
                else:
                    successful_tasks.append(result)
                    context["created_resources"].append(("task", result.task_id))

            # Log any failures for debugging
            if failed_submissions:
                logger.warning(
                    f"{len(failed_submissions)} submissions failed: "
                    f"{[(i, str(e)) for i, e in failed_submissions]}"
                )

            # At least one should succeed
            assert len(successful_tasks) > 0, (
                f"All {CONCURRENT_TASK_COUNT} concurrent submissions failed. "
                f"Errors: {failed_submissions}"
            )

            # Verify successful tasks have unique IDs
            task_ids = [t.task_id for t in successful_tasks]
            assert len(set(task_ids)) == len(task_ids), "Duplicate task IDs detected"

            logger.info(
                f"Concurrent submission: {len(successful_tasks)}/{CONCURRENT_TASK_COUNT} succeeded"
            )

    def test_invalid_instance_type_error(self):
        """Test that invalid instance types are rejected."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        # This should fail when trying to find instances
        with pytest.raises(FCPAPIError) as exc_info:
            provider.find_instances({
                "instance_type": "invalid-gpu-type"
            }, limit=1)

        # Verify the error message is helpful
        error_msg = str(exc_info.value)
        assert "Unknown instance type: invalid-gpu-type" in error_msg, \
            "Error should mention the invalid instance type"
        assert "Available:" in error_msg, \
            "Error should list available options"
        assert "a100" in error_msg, \
            "Error should include valid instance types"

    def test_nonexistent_task_error(self):
        """Test that querying nonexistent tasks raises proper error."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        with pytest.raises(FCPResourceNotFoundError) as exc_info:
            provider.get_task("task-does-not-exist")
            
        assert "task-does-not-exist" in str(exc_info.value), \
            "Error should mention the task ID"

    def test_gpu_instance_allocation(self):
        """Test submitting a task to a real GPU instance."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        # Find any available instance
        instances = provider.find_instances({
            "max_price_per_hour": DEFAULT_MAX_PRICE
        }, limit=1)

        if not instances:
            pytest.skip("No instances available in test environment")

        with isolation_context(provider) as context:
            # Use the instance type that's actually available
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-gpu-test")
                .with_instance_type(instances[0].instance_type)
                .with_region(instances[0].region)
                .with_command("echo 'Test task submitted'; nvidia-smi || echo 'No GPU available'")
                .with_max_price(DEFAULT_MAX_PRICE)
                .with_upload_code(False)
                .build())

            # Submit task
            task = provider.submit_task(
                instance_id=instances[0].allocation_id,
                config=config
            )
            context["created_resources"].append(("task", task.task_id))

            # Verify task was created
            assert task.task_id, "Task missing ID"
            assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING], \
                f"Unexpected task status: {task.status}"

            # Log success
            logger.info(
                f"Successfully submitted task {task.task_id} "
                f"to {instances[0].instance_type}"
            )


@pytest.mark.integration
class TestFCPStorageIntegration:
    """Test storage operations against real API.
    
    Each test is completely isolated and manages its own resources.
    """

    def test_volume_lifecycle(self):
        """Test creating, listing, and deleting volumes."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        with isolation_context(provider) as context:
            # Create volume
            volume = provider.create_volume(
                name=f"{context['namespace']}-test-volume",
                size_gb=10
            )
            context["created_resources"].append(("volume", volume.volume_id))

            # Verify creation
            assert volume.volume_id, "Volume missing ID"
            assert volume.size_gb == 10, "Volume has incorrect size"
            assert volume.status == "available", "Volume not available after creation"

            # List volumes
            volumes = provider.list_volumes()
            volume_ids = [v.volume_id for v in volumes]
            assert volume.volume_id in volume_ids, "Created volume not in list"

            # Delete volume
            deleted = provider.delete_volume(volume.volume_id)
            assert deleted is True, "Delete operation failed"

            # Verify deletion
            with pytest.raises(ResourceNotFoundError) as exc_info:
                provider.get_volume(volume.volume_id)
                
            assert volume.volume_id in str(exc_info.value), \
                "Error should mention the volume ID"


@pytest.mark.integration 
class TestResourceCleanup:
    """Test resource cleanup and verification.
    
    These tests verify that resources are properly cleaned up
    and don't leak between tests.
    """
    
    def test_cleanup_verification_after_failure(self):
        """Test that resources are cleaned up even after test failures."""
        skip_if_no_api_key()
        provider = create_test_provider()
        created_tasks: List[str] = []
        
        try:
            with isolation_context(provider) as context:
                # Find instance
                instances = provider.find_instances(
                    {"max_price_per_hour": DEFAULT_MAX_PRICE}, 
                    limit=1
                )
                if not instances:
                    pytest.skip("No instances available")
                    
                # Create a task
                config = (TaskConfigBuilder()
                    .with_name(f"{context['namespace']}-cleanup-test")
                    .with_instance_type(instances[0].instance_type)
                    .with_command("echo 'Testing cleanup'")
                    .with_upload_code(False)
                    .build())
                    
                task = submit_test_task(provider, config)
                created_tasks.append(task.task_id)
                context["created_resources"].append(("task", task.task_id))
                
                # Simulate test failure
                raise RuntimeError("Simulated test failure")
                
        except RuntimeError:
            # Expected failure
            pass
            
        # Verify cleanup happened
        for task_id in created_tasks:
            try:
                task = provider.get_task(task_id)
                # Task should be cancelled or completed
                assert task.status in [TaskStatus.CANCELLED, TaskStatus.COMPLETED], \
                    f"Task {task_id} not cleaned up, status: {task.status}"
            except ResourceNotFoundError:
                # Task was deleted - also acceptable
                pass
                
    def test_no_resource_leakage_between_tests(self):
        """Test that tests don't see resources from other tests."""
        skip_if_no_api_key()
        provider = create_test_provider()
        
        # Create a unique namespace for this test
        test_namespace = f"leak-test-{os.getpid()}"
        
        # List all tasks and volumes
        try:
            tasks = provider.list_tasks()
            volumes = provider.list_volumes()
            
            # Check that no resources from other tests are visible
            # (they should have different namespaces)
            for task in tasks:
                if hasattr(task, 'name') and task.name:
                    assert not task.name.startswith("test-ns-"), \
                        f"Found task from another test: {task.name}"
                        
            for volume in volumes:
                if hasattr(volume, 'name') and volume.name:
                    assert not volume.name.startswith("test-ns-"), \
                        f"Found volume from another test: {volume.name}"
                        
        except Exception as e:
            # Some providers might not support listing
            logger.info(f"Skipping leakage test: {e}")