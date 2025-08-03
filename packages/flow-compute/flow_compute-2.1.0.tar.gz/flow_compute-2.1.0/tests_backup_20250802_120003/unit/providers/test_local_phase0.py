"""Phase 0: Basic LocalProvider tests - Walking Skeleton."""

import time

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.providers.local.provider import LocalProvider


class TestLocalProviderPhase0:
    """Test the simplest possible LocalProvider functionality."""

    def test_hello_world(self):
        """The simplest possible test - can we run echo?"""
        provider = LocalProvider(Config(provider="local"))
        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            command="echo hello"
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        assert task.status == TaskStatus.COMPLETED
        assert "hello" in provider.get_task_logs(task.task_id)

    def test_command_execution(self):
        """Can we run a real command?"""
        provider = LocalProvider(Config(provider="local"))
        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            command=["python", "-c", "print('Python works')"]
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "Python works" in logs

    def test_failure_handling(self):
        """Do we handle failures correctly?"""
        provider = LocalProvider(Config(provider="local"))
        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            command="exit 1"
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        assert task.status == TaskStatus.FAILED

    def test_task_lifecycle(self):
        """Test basic task lifecycle tracking."""
        provider = LocalProvider(Config(provider="local"))

        # Submit task
        task = provider.submit_task("local", TaskConfig(
            name="lifecycle-test",
            instance_type="cpu.small",
            command="sleep 0.5; echo done"
        ))
        task_id = task.task_id

        # Should start as PENDING or quickly move to RUNNING
        assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

        # Get task by ID
        retrieved_task = provider.get_task(task_id)
        assert retrieved_task.task_id == task_id

        # Wait for completion
        for _ in range(20):
            time.sleep(0.1)
            task = provider.get_task(task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        # Should complete successfully
        assert task.status == TaskStatus.COMPLETED
        assert "done" in provider.get_task_logs(task_id)

    def test_environment_variables(self):
        """Test that environment variables are passed correctly."""
        provider = LocalProvider(Config(provider="local"))
        task = provider.submit_task("local", TaskConfig(
            name="env-test",
            instance_type="cpu.small",
            command="echo $MY_VAR",
            env={"MY_VAR": "test123"}
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "test123" in logs


if __name__ == "__main__":
    # Run tests directly
    test = TestLocalProviderPhase0()

    print("Running Phase 0 tests...")

    print("1. Testing hello world...")
    test.test_hello_world()
    print("✓ Hello world works")

    print("2. Testing command execution...")
    test.test_command_execution()
    print("✓ Command execution works")

    print("3. Testing failure handling...")
    test.test_failure_handling()
    print("✓ Failure handling works")

    print("4. Testing task lifecycle...")
    test.test_task_lifecycle()
    print("✓ Task lifecycle works")

    print("5. Testing environment variables...")
    test.test_environment_variables()
    print("✓ Environment variables work")

    print("\nAll Phase 0 tests passed! ✅")
