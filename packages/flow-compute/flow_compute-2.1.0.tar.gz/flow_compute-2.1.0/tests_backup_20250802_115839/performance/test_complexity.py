"""Algorithmic complexity verification tests."""

import statistics
import time
from typing import List

import pytest

from flow.api.models import CPUSpec, GPUSpec, InstanceType, MemorySpec, NetworkSpec, StorageSpec


class ComplexityTester:
    """Base class for complexity testing with proper methodology."""

    @staticmethod
    def measure_operation(operation, warmup_runs: int = 3, test_runs: int = 10) -> float:
        """Measure operation time with warmup and multiple runs.
        
        Args:
            operation: Callable to measure
            warmup_runs: Number of warmup runs to discard
            test_runs: Number of test runs to average
            
        Returns:
            Median time in seconds (more stable than mean)
        """
        # Warmup runs
        for _ in range(warmup_runs):
            operation()

        # Test runs
        times = []
        for _ in range(test_runs):
            start = time.perf_counter()
            operation()
            end = time.perf_counter()
            times.append(end - start)

        # Return median (more stable than mean for performance tests)
        return statistics.median(times)

    @staticmethod
    def verify_linear_complexity(
        sizes: List[int],
        operation_factory,
        tolerance: float = 3.0,
        min_ratio: float = 0.5
    ) -> None:
        """Verify an operation has linear O(n) complexity.
        
        Args:
            sizes: List of input sizes to test
            operation_factory: Function that creates operation for given size
            tolerance: Maximum allowed ratio between actual and expected growth
            min_ratio: Minimum ratio to consider (filters out noise)
        """
        measurements = []

        for size in sizes:
            operation = operation_factory(size)
            time_taken = ComplexityTester.measure_operation(operation)
            measurements.append((size, time_taken))

        # Verify complexity by checking growth rates
        for i in range(1, len(measurements)):
            prev_size, prev_time = measurements[i-1]
            curr_size, curr_time = measurements[i]

            size_ratio = curr_size / prev_size
            time_ratio = curr_time / prev_time

            # Skip if times are too small (noise dominates)
            if prev_time < 1e-6 or curr_time < 1e-6:
                continue

            # Skip if ratio is too small (measurement noise)
            if time_ratio < min_ratio:
                continue

            # Check that time grows roughly linearly with size
            assert time_ratio <= size_ratio * tolerance, (
                f"Non-linear growth detected: {curr_size}/{prev_size}={size_ratio:.1f}x size "
                f"caused {curr_time/prev_time:.1f}x time increase (tolerance={tolerance}x)"
            )


class TestAlgorithmicComplexity:
    """Test algorithmic complexity of critical operations."""

    def test_list_search_complexity(self):
        """Verify list search maintains O(n) complexity."""
        # Use larger sizes for stable measurements
        sizes = [1000, 5000, 10000]

        # Pre-create instances to avoid measuring object creation
        all_instances = []
        gpu_spec = GPUSpec(
            vendor="NVIDIA",
            model="A100",
            memory_gb=80,
            memory_type="HBM2e",
            architecture="Ampere",
            compute_capability=(8, 0),
            tflops_fp32=19.5,
            tflops_fp16=312.0,
            memory_bandwidth_gb_s=1555.0,
        )

        for i in range(max(sizes)):
            instance = InstanceType(
                gpu=gpu_spec,
                gpu_count=8,
                cpu=CPUSpec(cores=64, vendor="Intel", model="Xeon"),
                memory=MemorySpec(size_gb=512),
                storage=StorageSpec(size_gb=1000),
                network=NetworkSpec(intranode="SXM4"),
            )
            all_instances.append(instance)

        def create_search_operation(size: int):
            """Create search operation for given size."""
            instances = all_instances[:size]

            def search():
                # Actual search operation we're measuring
                return [i for i in instances if i.gpu and i.gpu.memory_gb >= 80]

            return search

        # Verify linear complexity
        ComplexityTester.verify_linear_complexity(
            sizes=sizes,
            operation_factory=create_search_operation,
            tolerance=3.0  # Allow 3x variance for linear complexity
        )

    def test_dict_lookup_complexity(self):
        """Verify dict lookup maintains O(1) complexity."""
        sizes = [1000, 10000, 100000]

        # Pre-create data
        all_data = {f"task-{i}": {"id": i, "status": "running"} for i in range(max(sizes))}

        def create_lookup_operation(size: int):
            """Create lookup operation for given size."""
            data = {k: v for k, v in list(all_data.items())[:size]}
            lookup_key = f"task-{size//2}"  # Middle element

            def lookup():
                # Multiple lookups to get measurable time
                for _ in range(1000):
                    _ = data.get(lookup_key)

            return lookup

        # For O(1) operations, time should not grow with size
        measurements = []
        for size in sizes:
            operation = create_lookup_operation(size)
            time_taken = ComplexityTester.measure_operation(operation)
            measurements.append((size, time_taken))

        # Verify constant time (allow 2x variance)
        base_time = measurements[0][1]
        for size, time_taken in measurements[1:]:
            assert time_taken < base_time * 2, (
                f"Dict lookup not O(1): {size} items took {time_taken:.6f}s "
                f"vs {measurements[0][0]} items took {base_time:.6f}s"
            )


@pytest.mark.benchmark
class TestPerformanceRegression:
    """Ensure critical operations don't regress in performance."""

    def test_instance_creation_performance(self):
        """Ensure instance creation stays fast."""
        def create_instance():
            return InstanceType(
                gpu=GPUSpec(
                    vendor="NVIDIA",
                    model="A100",
                    memory_gb=80,
                    memory_type="HBM2e",
                    architecture="Ampere",
                    compute_capability=(8, 0),
                    tflops_fp32=19.5,
                    tflops_fp16=312.0,
                    memory_bandwidth_gb_s=1555.0,
                ),
                gpu_count=8,
                cpu=CPUSpec(cores=64, vendor="Intel", model="Xeon"),
                memory=MemorySpec(size_gb=512),
                storage=StorageSpec(size_gb=1000),
                network=NetworkSpec(intranode="SXM4"),
            )

        # Measure time for 1000 creations
        start = time.perf_counter()
        for _ in range(1000):
            create_instance()
        end = time.perf_counter()

        total_time = end - start
        per_instance_time = total_time / 1000

        # Should be fast (< 100μs per instance)
        assert per_instance_time < 0.0001, (
            f"Instance creation too slow: {per_instance_time*1e6:.1f}μs per instance"
        )
