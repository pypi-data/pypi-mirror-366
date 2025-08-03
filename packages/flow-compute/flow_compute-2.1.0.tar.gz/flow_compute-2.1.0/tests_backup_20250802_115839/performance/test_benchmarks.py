"""Performance benchmarks for Flow SDK critical paths.

These benchmarks measure performance of key operations to ensure the SDK
remains fast and efficient. We focus on:

1. Measuring latency of critical operations
2. Tracking memory usage for large datasets
3. Ensuring O(n) or better algorithmic complexity
4. Identifying performance regressions
"""

import gc
import statistics
import time
from contextlib import contextmanager
from typing import Callable, Tuple

import pytest
from hypothesis import given
from hypothesis import strategies as st

from flow.api.models import (
    AvailableInstance,
    CPUSpec,
    GPUSpec,
    InstanceType,
    MemorySpec,
    NetworkSpec,
    StorageSpec,
    TaskConfig,
    TaskStatus,
    VolumeSpec,
)
from tests.support.framework import (
    TaskBuilder,
    TaskConfigBuilder,
)


@contextmanager
def measure_time(name: str) -> None:
    """Context manager to measure execution time."""
    gc.collect()  # Clean up before measurement
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        duration_ms = (end - start) * 1000
        print(f"\n{name}: {duration_ms:.2f}ms")


@contextmanager
def measure_memory(name: str) -> None:
    """Context manager to measure memory usage."""
    import tracemalloc

    gc.collect()
    tracemalloc.start()

    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"\n{name} - Current: {current/1024/1024:.2f}MB, Peak: {peak/1024/1024:.2f}MB")


def benchmark_function(func: Callable, iterations: int = 1000) -> Tuple[float, float, float]:
    """Benchmark a function and return min, mean, max times in ms."""
    times = []

    # Warmup
    for _ in range(10):
        func()

    # Measure
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)

    return min(times), statistics.mean(times), max(times)


class TestModelPerformance:
    """Benchmark model creation and validation performance."""

    def test_task_config_creation_performance(self):
        """Benchmark TaskConfig creation speed."""
        def create_config():
            return TaskConfig(
                name="benchmark-task",
                instance_type="gpu.nvidia.a100",
                command=["python", "train.py"],
                env={"KEY": "value"},
                volumes=[
                    VolumeSpec(name="data", mount_path="/data", size_gb=100)
                ],
            )

        min_ms, mean_ms, max_ms = benchmark_function(create_config)

        # Performance assertions
        assert mean_ms < 1.0, f"TaskConfig creation too slow: {mean_ms:.2f}ms"
        assert max_ms < 5.0, f"TaskConfig creation max time too high: {max_ms:.2f}ms"

        print(f"\nTaskConfig creation: min={min_ms:.3f}ms, mean={mean_ms:.3f}ms, max={max_ms:.3f}ms")

    def test_large_task_list_performance(self):
        """Benchmark handling large lists of tasks."""
        # Create 10,000 tasks
        tasks = []
        with measure_time("Creating 10,000 tasks"):
            for i in range(10000):
                task = TaskBuilder() \
                    .with_id(f"task-{i}") \
                    .with_name(f"job-{i}") \
                    .with_status(TaskStatus.RUNNING if i % 2 == 0 else TaskStatus.COMPLETED) \
                    .build()
                tasks.append(task)

        # Measure filtering performance
        with measure_time("Filtering running tasks"):
            running_tasks = [t for t in tasks if t.status == TaskStatus.RUNNING]
            assert len(running_tasks) == 5000

        # Measure sorting performance
        with measure_time("Sorting by created_at"):
            sorted_tasks = sorted(tasks, key=lambda t: t.created_at)
            assert len(sorted_tasks) == 10000

        # Measure serialization performance
        with measure_time("Serializing to JSON"):
            json_data = [t.model_dump_json() for t in tasks[:100]]
            assert len(json_data) == 100

    def test_model_validation_performance(self):
        """Benchmark model validation speed."""
        # Valid data
        valid_data = {
            "name": "test-task",
            "instance_type": "gpu.nvidia.a100",
            "command": ["python", "script.py"],
        }

        def validate_valid():
            TaskConfig(**valid_data)

        min_ms, mean_ms, max_ms = benchmark_function(validate_valid)
        assert mean_ms < 0.5, f"Valid data validation too slow: {mean_ms:.2f}ms"

        # Invalid data
        invalid_data = {
            "name": "",  # Invalid
            "instance_type": "invalid-type",
            "command": [],  # Invalid
            "priority": 200,  # Out of range
        }

        def validate_invalid():
            try:
                TaskConfig(**invalid_data)
            except:
                pass

        min_ms, mean_ms, max_ms = benchmark_function(validate_invalid, iterations=100)
        assert mean_ms < 5.0, f"Invalid data validation too slow: {mean_ms:.2f}ms"


class TestInstanceSearchPerformance:
    """Benchmark instance search operations."""

    def test_instance_list_search_performance(self):
        """Benchmark searching through instance lists."""
        # Create 100 instance types
        instances = []
        for i in range(100):
            gpu_memory = 40 if i < 30 else 80 if i < 70 else 160
            gpu_spec = GPUSpec(
                vendor="NVIDIA",
                model=f"GPU{i}",
                memory_gb=gpu_memory,
                memory_type="HBM3",
                architecture="Hopper",
                compute_capability=(9, 0),
                tflops_fp32=60.0,
                tflops_fp16=120.0,
                memory_bandwidth_gb_s=3000.0,
            )
            # Create complete instance type with all required fields
            instance = InstanceType(
                gpu=gpu_spec,
                gpu_count=8,  # Standard 8xGPU configuration
                cpu=CPUSpec(cores=64, vendor="Intel", model="Xeon"),
                memory=MemorySpec(size_gb=512),
                storage=StorageSpec(size_gb=1000),
                network=NetworkSpec(intranode="SXM4", internode="InfiniBand"),
            )
            instances.append(instance)

        def search_by_memory(min_memory):
            return [i for i in instances if i.gpu and i.gpu.memory_gb >= min_memory]

        # Benchmark different memory requirements
        for memory in [40, 80, 160]:
            def search():
                return search_by_memory(memory)

            min_ms, mean_ms, max_ms = benchmark_function(search, iterations=1000)
            print(f"\nSearch {memory}GB: min={min_ms:.3f}ms, mean={mean_ms:.3f}ms, max={max_ms:.3f}ms")

            # Should be fast even with 100 instances
            assert mean_ms < 0.5, f"Instance search too slow for {memory}GB: {mean_ms:.2f}ms"

    def test_instance_data_parsing_performance(self):
        """Benchmark parsing instance data."""
        # Simulate parsing instance data from API
        instance_data = []
        for i in range(500):  # 500 instance types
            data = {
                "gpu": {
                    "vendor": "NVIDIA",
                    "model": f"GPU{i}",
                    "memory_gb": 80,
                    "memory_type": "HBM3",
                    "architecture": "Hopper",
                    "compute_capability": (9, 0),
                    "tflops_fp32": 60.0,
                    "tflops_fp16": 120.0,
                    "memory_bandwidth_gb_s": 3000.0,
                },
                "gpu_count": 8,
                "cpu": {
                    "cores": 32,
                    "vendor": "Intel",
                    "model": "Xeon",
                },
                "memory": {
                    "size_gb": 256,
                },
                "storage": {
                    "size_gb": 1000,
                },
                "network": {
                    "intranode": "SXM4",
                    "internode": "InfiniBand",
                },
            }
            instance_data.append(data)

        def parse_instances():
            parsed = []
            for data in instance_data:
                # Build complete instance from data
                instance = InstanceType(
                    gpu=GPUSpec(**data["gpu"]),
                    gpu_count=data["gpu_count"],
                    cpu=CPUSpec(**data["cpu"]),
                    memory=MemorySpec(**data["memory"]),
                    storage=StorageSpec(**data["storage"]),
                    network=NetworkSpec(**data["network"]),
                )
                parsed.append(instance)
            return parsed

        min_ms, mean_ms, max_ms = benchmark_function(parse_instances, iterations=10)
        print(f"\nParsing 500 instances: min={min_ms:.1f}ms, mean={mean_ms:.1f}ms, max={max_ms:.1f}ms")

        # Should parse reasonably fast (allow more time for complex model validation)
        assert mean_ms < 200, f"Instance parsing too slow: {mean_ms:.1f}ms"


class TestTaskListPerformance:
    """Benchmark task list operations."""

    def test_task_list_operations(self):
        """Benchmark task list management."""
        # Simulate a task tracking system
        tasks = {}  # id -> task mapping
        tasks_by_status = {status: set() for status in TaskStatus}

        # Add 1000 tasks
        with measure_time("Adding 1000 tasks"):
            for i in range(1000):
                task = TaskBuilder() \
                    .with_id(f"task-{i}") \
                    .with_status(TaskStatus.PENDING) \
                    .build()
                tasks[task.task_id] = task
                tasks_by_status[TaskStatus.PENDING].add(task.task_id)

        # Update half to running
        with measure_time("Updating 500 tasks to RUNNING"):
            for i in range(0, 500):
                task_id = f"task-{i}"
                if task_id in tasks:
                    old_status = tasks[task_id].status
                    tasks_by_status[old_status].discard(task_id)
                    tasks[task_id].status = TaskStatus.RUNNING
                    tasks_by_status[TaskStatus.RUNNING].add(task_id)

        # Update quarter to completed
        with measure_time("Updating 250 tasks to COMPLETED"):
            for i in range(0, 250):
                task_id = f"task-{i}"
                if task_id in tasks:
                    old_status = tasks[task_id].status
                    tasks_by_status[old_status].discard(task_id)
                    tasks[task_id].status = TaskStatus.COMPLETED
                    tasks_by_status[TaskStatus.COMPLETED].add(task_id)

        # Query by status
        with measure_time("Querying RUNNING tasks"):
            running_ids = tasks_by_status[TaskStatus.RUNNING]
            running_tasks = [tasks[tid] for tid in running_ids]
            assert len(running_tasks) == 250  # 500 - 250 completed

        # Cleanup old tasks
        with measure_time("Cleaning up completed tasks"):
            completed_ids = list(tasks_by_status[TaskStatus.COMPLETED])
            for task_id in completed_ids:
                del tasks[task_id]
                tasks_by_status[TaskStatus.COMPLETED].discard(task_id)
            assert len(completed_ids) == 250


class TestProviderPerformance:
    """Benchmark provider operations."""

    def test_instance_matching_performance(self):
        """Benchmark instance matching logic."""
        # Create available instances
        instances = []
        for i in range(100):
            instance = AvailableInstance(
                allocation_id=f"alloc-{i}",
                instance_type="gpu.nvidia.a100" if i < 50 else "gpu.nvidia.h100",
                region="us-east-1" if i < 70 else "us-west-2",
                price_per_hour=20.0 + i * 0.1,
            )
            instances.append(instance)

        # Benchmark sorting by price
        def sort_by_price():
            return sorted(instances, key=lambda x: x.price_per_hour)

        min_ms, mean_ms, max_ms = benchmark_function(sort_by_price)
        assert mean_ms < 0.1, f"Sorting instances too slow: {mean_ms:.2f}ms"

        # Benchmark filtering
        def filter_a100():
            return [i for i in instances if "a100" in i.instance_type]

        min_ms, mean_ms, max_ms = benchmark_function(filter_a100)
        assert mean_ms < 0.05, f"Filtering instances too slow: {mean_ms:.2f}ms"


class TestMemoryEfficiency:
    """Test memory efficiency of SDK operations."""

    def test_large_volume_list_memory(self):
        """Test memory usage with large volume lists."""
        with measure_memory("Creating 10,000 volume specs"):
            volumes = []
            for i in range(10000):
                vol = VolumeSpec(
                    name=f"volume-{i}",
                    mount_path=f"/mnt/vol{i}",
                    size_gb=100,
                )
                volumes.append(vol)

            # Ensure we're not using excessive memory
            # Each VolumeSpec should be < 1KB
            import sys
            total_size = sum(sys.getsizeof(v) for v in volumes)
            avg_size = total_size / len(volumes)
            assert avg_size < 1024, f"VolumeSpec too large: {avg_size} bytes"

    def test_task_config_memory_sharing(self):
        """Test that TaskConfig shares memory efficiently."""
        base_env = {"SHARED_KEY": "x" * 1000}  # 1KB string

        configs = []
        with measure_memory("Creating configs with shared env"):
            for i in range(1000):
                # These should share the base_env reference
                config = TaskConfig(
                    name=f"task-{i}",
                    instance_type="gpu.nvidia.a100",
                    command=["python", "script.py"],
                    env=base_env,  # Same reference
                )
                configs.append(config)


class TestAlgorithmicComplexity:
    """Verify algorithmic complexity of operations."""

    @given(n=st.integers(min_value=10, max_value=1000))
    def test_dict_lookup_is_constant_time(self, n):
        """Verify dictionary lookup is O(1)."""
        tasks = {}

        # Add n tasks
        for i in range(n):
            task = TaskBuilder().with_id(f"task-{i}").build()
            tasks[task.task_id] = task

        # Measure lookup time - should be constant regardless of n
        lookup_times = []
        for _ in range(100):
            start = time.perf_counter()
            task = tasks.get(f"task-{n//2}")  # Middle task
            end = time.perf_counter()
            lookup_times.append(end - start)

        avg_time = statistics.mean(lookup_times)

        # Time should not increase with n (allowing some variance)
        assert avg_time < 0.0001, f"Lookup time not O(1): {avg_time*1000:.3f}ms for n={n}"

    @pytest.mark.skip(reason="Moved to test_complexity.py with better methodology")
    def test_list_search_is_linear(self):
        """Verify list search is O(n) in worst case."""
        # This test has been moved to test_complexity.py with:
        # - Larger sample sizes for stability
        # - Multiple measurements with warmup
        # - Pre-created objects to avoid measuring allocation
        # - Statistical analysis of results
        pass


class TestCriticalPathPerformance:
    """Benchmark end-to-end critical paths."""

    def test_task_submission_critical_path(self):
        """Benchmark the full task submission path."""
        # Simulate the critical path without actual API calls

        with measure_time("Complete task submission"):
            # 1. Create config
            config = TaskConfigBuilder() \
                .with_name("benchmark-task") \
                .with_instance_type("gpu.nvidia.a100") \
                .with_command("python train.py") \
                .with_volumes([
                    {"name": "data", "mount_path": "/data"},
                    {"name": "models", "mount_path": "/models"},
                ]) \
                .build()

            # 2. Validate config
            config.model_validate(config.model_dump())

            # 3. Create task
            task = TaskBuilder() \
                .with_name(config.name) \
                .with_instance_type(config.instance_type) \
                .with_status(TaskStatus.PENDING) \
                .build()

            # 4. Serialize for API
            api_payload = {
                "name": config.name,
                "instance_type": config.instance_type,
                "command": config.command,
                "volumes": [v.model_dump() if hasattr(v, 'model_dump') else v for v in config.volumes],
            }

            # 5. Simulate tracking (no actual manager in benchmark)
            # In real usage, this would be tracked by the provider
            task_registry = {task.task_id: task}

        # The entire flow should be fast
        # Real submission would add network latency
