"""Phase 1: Async execution tests for LocalProvider."""

import time

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.providers.local.provider import LocalProvider


class TestLocalProviderPhase1:
    """Test async execution capabilities."""

    def test_async_execution(self):
        """Task should return immediately."""
        provider = LocalProvider(Config(provider="local"))

        start = time.time()
        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            command="sleep 1"
        ))
        elapsed = time.time() - start

        assert elapsed < 0.1  # Should return immediately
        assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

        # Wait for completion
        for _ in range(30):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        assert task.status == TaskStatus.COMPLETED

    def test_concurrent_tasks(self):
        """Can run multiple tasks concurrently."""
        provider = LocalProvider(Config(provider="local"))

        # Submit multiple tasks
        tasks = []
        start = time.time()
        for i in range(3):
            task = provider.submit_task("local", TaskConfig(
                name=f"test-{i}",
                instance_type="cpu.small",
                command=f"sleep 0.5; echo task-{i}"
            ))
            tasks.append(task)
        submit_time = time.time() - start

        # Submission should be fast
        assert submit_time < 0.3  # 3 tasks should submit in < 0.3s

        # All should be running or pending
        time.sleep(0.1)
        for task in tasks:
            task = provider.get_task(task.task_id)
            assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

        # All should complete
        time.sleep(1.5)  # Give enough time for all to complete
        for i, task in enumerate(tasks):
            task = provider.get_task(task.task_id)
            assert task.status == TaskStatus.COMPLETED
            logs = provider.get_task_logs(task.task_id)
            assert f"task-{i}" in logs

    def test_immediate_return(self):
        """Submit returns immediately even for long-running tasks."""
        provider = LocalProvider(Config(provider="local"))

        # Submit a long-running task
        start = time.time()
        task = provider.submit_task("local", TaskConfig(
            name="long-task",
            instance_type="cpu.small",
            command="sleep 5; echo done"
        ))
        submit_time = time.time() - start

        # Should return immediately
        assert submit_time < 0.1
        assert task.task_id.startswith("local-")
        assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

        # Stop the task to clean up
        provider.stop_task(task.task_id)

    def test_task_isolation(self):
        """Tasks should be isolated from each other."""
        provider = LocalProvider(Config(provider="local"))

        # Submit tasks with different outputs
        task1 = provider.submit_task("local", TaskConfig(
            name="task1",
            instance_type="cpu.small",
            command="echo 'Output from task 1'"
        ))

        task2 = provider.submit_task("local", TaskConfig(
            name="task2",
            instance_type="cpu.small",
            command="echo 'Output from task 2'"
        ))

        # Wait for both to complete
        time.sleep(1)

        # Check logs are separate
        logs1 = provider.get_task_logs(task1.task_id)
        logs2 = provider.get_task_logs(task2.task_id)

        assert "Output from task 1" in logs1
        assert "Output from task 2" not in logs1
        assert "Output from task 2" in logs2
        assert "Output from task 1" not in logs2

    def test_performance_benchmark(self):
        """Benchmark task submission performance."""
        provider = LocalProvider(Config(provider="local"))

        # Submit 10 tasks and measure time
        start = time.time()
        tasks = []
        for i in range(10):
            task = provider.submit_task("local", TaskConfig(
                name=f"perf-{i}",
                instance_type="cpu.small",
                command=f"echo 'Task {i}'"
            ))
            tasks.append(task)

        elapsed = time.time() - start
        avg_submit_time = elapsed / 10

        print(f"\n✓ Performance: Submitted 10 tasks in {elapsed:.3f}s")
        print(f"✓ Average submit time: {avg_submit_time:.3f}s per task")

        # Should be very fast
        assert avg_submit_time < 0.05  # <50ms per task submission

        # Clean up
        for task in tasks:
            try:
                provider.stop_task(task.task_id)
            except:
                pass


if __name__ == "__main__":
    # Run tests directly
    test = TestLocalProviderPhase1()

    print("Running Phase 1 tests...")

    print("1. Testing async execution...")
    test.test_async_execution()
    print("✓ Async execution works")

    print("2. Testing concurrent tasks...")
    test.test_concurrent_tasks()
    print("✓ Concurrent tasks work")

    print("3. Testing immediate return...")
    test.test_immediate_return()
    print("✓ Immediate return works")

    print("4. Testing task isolation...")
    test.test_task_isolation()
    print("✓ Task isolation works")

    print("5. Running performance benchmark...")
    test.test_performance_benchmark()
    print("✓ Performance meets requirements")

    print("\nAll Phase 1 tests passed! ✅")
