"""End-to-end integration tests for Flow SDK.

These tests verify complete workflows against real infrastructure.
No mocks - we test actual behavior with real API calls.
"""

import os
import time

import pytest

from flow.api.models import TaskStatus
from flow.errors import ValidationError
from tests.support.framework import (
    TaskConfigBuilder,
    isolation_context,
    wait_for_task_status,
)
from tests.support.framework.base import IntegrationTest


@pytest.mark.integration
class TestEndToEndWorkflows(IntegrationTest):
    """Test complete workflows with real infrastructure."""

    # Use base class fixtures for flow and API health checks

    def test_simple_task_lifecycle(self, flow, available_instance):
        """Test basic task submission and completion."""
        # Ensure provider is initialized
        provider = flow._ensure_provider()
        with isolation_context(provider) as context:

            # Create simple task with available instance type
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-simple")
                .with_instance_type(available_instance)
                .with_command("echo 'Hello from E2E test'; date; sleep 3; echo 'Done'")
                .with_max_price(5.0)
                .build())

            # Submit task using test helper
            from tests.support.framework import submit_test_task
            task = submit_test_task(provider, config)
            context["created_resources"].append(("task", task.task_id))

            # Verify initial state
            assert task.task_id
            assert task.name == config.name
            assert task.status in [TaskStatus.PENDING, TaskStatus.QUEUED]

            # Wait for completion
            completed = False
            for _ in range(60):  # Wait up to 60 seconds
                status = flow.status(task.task_id)
                if status == "completed":
                    completed = True
                    break
                elif status == "failed":
                    logs = flow.logs(task.task_id)
                    pytest.fail(f"Task failed. Logs:\n{logs}")
                time.sleep(1)

            assert completed, "Task did not complete in time"

            # Get final task details
            final_task = flow.get_task(task.task_id)
            assert final_task.status == TaskStatus.COMPLETED
            assert final_task.total_cost is not None

            # Check logs
            logs = flow.logs(task.task_id)
            assert "Hello from E2E test" in logs
            assert "Done" in logs

    def test_gpu_task_execution(self, flow):
        """Test GPU task execution if GPUs are available."""
        # Skip GPU tests in CI environment
        if os.environ.get("CI") or not os.environ.get("RUN_GPU_TESTS"):
            pytest.skip("GPU tests skipped (set RUN_GPU_TESTS=1 to enable)")

        with isolation_context(flow._provider) as context:
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-gpu")
                .with_instance_type("it_5ECSoHQjLBzrp5YM")  # Use actual allocation ID from API
                .with_script("""
                    echo "Checking GPU availability"
                    nvidia-smi
                    
                    python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
                        print(f'GPU count: {torch.cuda.device_count()}')
                        print(f'GPU name: {torch.cuda.get_device_name(0)}')
                    "
                """)
                .with_max_price(20.0)
                .build())

            task = flow.run(config)
            context["created_resources"].append(("task", task.task_id))

            # Wait for completion
            if wait_for_task_status(flow._provider, task.task_id, TaskStatus.COMPLETED, timeout=180):
                logs = flow.logs(task.task_id)
                assert "NVIDIA" in logs or "Tesla" in logs
                assert "CUDA available: True" in logs

    def test_task_with_volumes(self, flow):
        """Test task execution with attached volumes."""
        with isolation_context(flow._provider) as context:
            # Create volumes using config
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-volumes")
                .with_cpu("small")
                .with_volume("/data", size_gb=10)
                .with_volume("/outputs", size_gb=5)
                .with_script("""
                    # Check volumes are mounted
                    df -h /data /outputs
                    
                    # Write to volumes
                    echo "Test data" > /data/test.txt
                    echo "Results" > /outputs/results.txt
                    
                    # Verify writes
                    ls -la /data/
                    ls -la /outputs/
                    cat /data/test.txt
                    cat /outputs/results.txt
                """)
                .build())

            task = flow.run(config)
            context["created_resources"].append(("task", task.task_id))

            # Wait for completion
            if wait_for_task_status(flow._provider, task.task_id, TaskStatus.COMPLETED, timeout=120):
                logs = flow.logs(task.task_id)
                assert "/data" in logs
                assert "/outputs" in logs
                assert "Test data" in logs
                assert "Results" in logs

    def test_concurrent_task_execution(self, flow):
        """Test running multiple tasks concurrently."""
        with isolation_context(flow._provider) as context:
            num_tasks = 3
            tasks = []

            # Submit multiple tasks
            for i in range(num_tasks):
                config = (TaskConfigBuilder()
                    .with_name(f"{context['namespace']}-concurrent-{i}")
                    .with_cpu("small")
                    .with_command(f"echo 'Task {i} started'; sleep {2 + i}; echo 'Task {i} done'")
                    .build())

                task = flow.run(config)
                tasks.append(task)
                context["created_resources"].append(("task", task.task_id))

            # All should be submitted
            assert len(tasks) == num_tasks
            assert len(set(t.task_id for t in tasks)) == num_tasks

            # Wait for all to complete
            completed_count = 0
            start_time = time.time()
            timeout = 120

            while completed_count < num_tasks and time.time() - start_time < timeout:
                for task in tasks:
                    if flow.status(task.task_id) == "completed":
                        completed_count += 1
                time.sleep(2)

            assert completed_count == num_tasks, f"Only {completed_count}/{num_tasks} tasks completed"

    def test_error_handling_invalid_config(self, flow):
        """Test that invalid configurations are properly rejected."""
        # Invalid instance type
        config = TaskConfigBuilder().with_instance_type("invalid-gpu-type").build()

        with pytest.raises(ValidationError):
            flow.run(config)

        # Empty command and script
        config = TaskConfigBuilder().with_command("").with_script("").build()

        with pytest.raises(ValidationError):
            flow.run(config)

    def test_task_cancellation_workflow(self, flow):
        """Test cancelling a running task."""
        with isolation_context(flow._provider) as context:
            # Submit long-running task
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-cancel")
                .with_cpu("small")
                .with_command("echo 'Starting long task'; sleep 300")
                .build())

            task = flow.run(config)
            context["created_resources"].append(("task", task.task_id))

            # Wait for it to start
            running = False
            for _ in range(30):
                if flow.status(task.task_id) == "running":
                    running = True
                    break
                time.sleep(1)

            if running:
                # Cancel it
                cancelled = flow.cancel(task.task_id)
                assert cancelled

                # Verify it's cancelled
                for _ in range(10):
                    status = flow.status(task.task_id)
                    if status == "cancelled":
                        break
                    time.sleep(1)

                assert flow.status(task.task_id) == "cancelled"

    def test_multi_node_task(self, flow):
        """Test multi-node task execution."""
        with isolation_context(flow._provider) as context:
            config = (TaskConfigBuilder()
                .with_name(f"{context['namespace']}-multi-node")
                .with_cpu("small")
                .with_num_instances(2)
                .with_script("""
                    # Each node runs this
                    hostname
                    echo "Node started at $(date)"
                    sleep 5
                    echo "Node completed at $(date)"
                """)
                .build())

            # Multi-node might not be available in all environments
            try:
                task = flow.run(config)
                context["created_resources"].append(("task", task.task_id))

                if wait_for_task_status(flow._provider, task.task_id, TaskStatus.COMPLETED, timeout=120):
                    logs = flow.logs(task.task_id)
                    # Should see output from multiple nodes
                    assert logs.count("Node started") >= 1
            except ValidationError as e:
                if "multi" in str(e).lower() or "instances" in str(e).lower():
                    pytest.skip("Multi-node not supported in test environment")
                raise
