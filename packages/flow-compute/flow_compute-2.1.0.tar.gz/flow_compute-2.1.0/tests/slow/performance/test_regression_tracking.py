"""Performance regression tracking with baseline measurements.

This module establishes performance baselines and detects regressions
in critical SDK operations. It tracks:
- Execution time for key operations
- Memory usage patterns
- Throughput metrics
- Resource utilization

Baselines are stored and compared across test runs to catch regressions early.
"""

import gc
import json
import os
import statistics
import time
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Callable
import psutil
import pytest

from flow.api.models import Task, TaskStatus, TaskConfig
from flow.providers.fcp.provider import FCPProvider
from flow.utils.cache import TTLCache


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    timestamp: float
    
    def is_regression(self, baseline: 'PerformanceBaseline', threshold: float = 0.2) -> bool:
        """Check if this metric represents a regression from baseline."""
        # Allow 20% degradation by default
        return (
            self.duration_ms > baseline.mean_duration_ms * (1 + threshold) or
            self.memory_mb > baseline.mean_memory_mb * (1 + threshold)
        )


@dataclass
class PerformanceBaseline:
    """Baseline measurements for an operation."""
    
    operation: str
    mean_duration_ms: float
    std_duration_ms: float
    mean_memory_mb: float
    std_memory_mb: float
    mean_cpu_percent: float
    samples: int
    last_updated: float
    
    @classmethod
    def from_metrics(cls, operation: str, metrics: List[PerformanceMetric]) -> 'PerformanceBaseline':
        """Create baseline from a list of metrics."""
        durations = [m.duration_ms for m in metrics]
        memories = [m.memory_mb for m in metrics]
        cpu_percents = [m.cpu_percent for m in metrics]
        
        return cls(
            operation=operation,
            mean_duration_ms=statistics.mean(durations),
            std_duration_ms=statistics.stdev(durations) if len(durations) > 1 else 0,
            mean_memory_mb=statistics.mean(memories),
            std_memory_mb=statistics.stdev(memories) if len(memories) > 1 else 0,
            mean_cpu_percent=statistics.mean(cpu_percents),
            samples=len(metrics),
            last_updated=time.time()
        )


class PerformanceTracker:
    """Track and compare performance metrics."""
    
    def __init__(self, baseline_file: Optional[Path] = None):
        """Initialize tracker with optional baseline file."""
        self.baseline_file = baseline_file or Path("tests/performance/.baselines.json")
        self.current_metrics: Dict[str, List[PerformanceMetric]] = {}
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self._load_baselines()
    
    def _load_baselines(self):
        """Load baselines from file."""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file) as f:
                    data = json.load(f)
                    self.baselines = {
                        k: PerformanceBaseline(**v)
                        for k, v in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load baselines: {e}")
    
    def _save_baselines(self):
        """Save baselines to file."""
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.baseline_file, 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.baselines.items()},
                f,
                indent=2
            )
    
    @contextmanager
    def measure(self, operation: str):
        """Measure performance of an operation."""
        # Get initial state
        process = psutil.Process()
        gc.collect()
        
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = process.cpu_percent(interval=0.1)
        
        start = time.perf_counter()
        
        try:
            yield
        finally:
            # Measure final state
            end = time.perf_counter()
            duration_ms = (end - start) * 1000
            
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            cpu_after = process.cpu_percent(interval=0.1)
            
            metric = PerformanceMetric(
                operation=operation,
                duration_ms=duration_ms,
                memory_mb=max(mem_after - mem_before, 0),  # Memory delta
                cpu_percent=(cpu_before + cpu_after) / 2,
                timestamp=time.time()
            )
            
            # Record metric
            if operation not in self.current_metrics:
                self.current_metrics[operation] = []
            self.current_metrics[operation].append(metric)
            
            # Check for regression
            if operation in self.baselines:
                baseline = self.baselines[operation]
                if metric.is_regression(baseline):
                    print(f"\nWARNING: Performance regression detected in '{operation}':")
                    print(f"  Duration: {metric.duration_ms:.2f}ms (baseline: {baseline.mean_duration_ms:.2f}ms)")
                    print(f"  Memory: {metric.memory_mb:.2f}MB (baseline: {baseline.mean_memory_mb:.2f}MB)")
    
    def update_baselines(self, force: bool = False):
        """Update baselines with current metrics."""
        for operation, metrics in self.current_metrics.items():
            if force or operation not in self.baselines:
                self.baselines[operation] = PerformanceBaseline.from_metrics(operation, metrics)
        self._save_baselines()
    
    def report(self) -> Dict[str, dict]:
        """Generate performance report."""
        report = {}
        
        for operation, metrics in self.current_metrics.items():
            baseline = self.baselines.get(operation)
            current = PerformanceBaseline.from_metrics(operation, metrics)
            
            report[operation] = {
                "current": {
                    "duration_ms": current.mean_duration_ms,
                    "memory_mb": current.mean_memory_mb,
                    "cpu_percent": current.mean_cpu_percent,
                    "samples": current.samples
                }
            }
            
            if baseline:
                report[operation]["baseline"] = {
                    "duration_ms": baseline.mean_duration_ms,
                    "memory_mb": baseline.mean_memory_mb,
                    "cpu_percent": baseline.mean_cpu_percent,
                    "samples": baseline.samples
                }
                report[operation]["change"] = {
                    "duration_pct": ((current.mean_duration_ms / baseline.mean_duration_ms) - 1) * 100,
                    "memory_pct": ((current.mean_memory_mb / baseline.mean_memory_mb) - 1) * 100
                }
        
        return report


# Global tracker instance
tracker = PerformanceTracker()


class TestPerformanceRegression:
    """Test suite for tracking performance regressions."""
    
    @pytest.fixture
    def sample_tasks(self) -> List[Task]:
        """Create sample tasks for testing."""
        tasks = []
        for i in range(100):
            task = Task(
                task_id=f"task-{i}",
                name=f"test-task-{i}",
                status=TaskStatus.RUNNING if i % 2 == 0 else TaskStatus.COMPLETED,
                created_at=datetime.now(timezone.utc),
                instance_type="gpu.a100" if i % 3 == 0 else "cpu.large",
                num_instances=1 + (i % 3),
                region="us-central1",
                cost_per_hour=f"${1.5 * (i % 5 + 1):.2f}"
            )
            tasks.append(task)
        return tasks
    
    def test_task_creation_performance(self):
        """Measure task object creation performance."""
        with tracker.measure("task_creation"):
            for i in range(1000):
                task = Task(
                    task_id=f"task-{i}",
                    name=f"test-{i}",
                    status=TaskStatus.RUNNING,
                    created_at=datetime.now(timezone.utc),
                    instance_type="cpu.small",
                    num_instances=1,
                    region="us-central1",
                    cost_per_hour="$1.00"
                )
    
    def test_task_list_filtering(self, sample_tasks):
        """Measure task list filtering performance."""
        # Test status filtering
        with tracker.measure("task_filter_by_status"):
            running_tasks = [t for t in sample_tasks if t.status == TaskStatus.RUNNING]
            assert len(running_tasks) == 50
        
        # Test name pattern filtering
        with tracker.measure("task_filter_by_name"):
            matched_tasks = [t for t in sample_tasks if "task-1" in t.name]
            assert len(matched_tasks) > 0
        
        # Test complex filtering
        with tracker.measure("task_filter_complex"):
            filtered = [
                t for t in sample_tasks
                if t.status == TaskStatus.RUNNING
                and t.instance_type.startswith("gpu")
                and t.num_instances > 1
            ]
            assert len(filtered) > 0
    
    def test_cache_performance(self):
        """Measure cache operation performance."""
        cache = TTLCache(ttl_seconds=300, max_size=1000)
        
        # Measure write performance
        with tracker.measure("cache_write_1000"):
            for i in range(1000):
                cache.set(f"key-{i}", f"value-{i}")
        
        # Measure read performance (hits)
        with tracker.measure("cache_read_hits_1000"):
            for i in range(1000):
                value = cache.get(f"key-{i}")
                assert value == f"value-{i}"
        
        # Measure read performance (misses)
        with tracker.measure("cache_read_misses_1000"):
            for i in range(1000, 2000):
                value = cache.get(f"key-{i}")
                assert value is None
        
        # Measure eviction performance
        with tracker.measure("cache_eviction"):
            # Fill cache beyond max size
            for i in range(2000):
                cache.set(f"evict-key-{i}", f"evict-value-{i}")
    
    def test_task_config_validation(self):
        """Measure task configuration validation performance."""
        configs = []
        
        # Create various config patterns
        for i in range(100):
            config = TaskConfig(
                name=f"test-task-{i}",
                command=["python", "script.py"],
                instance_type="gpu.a100" if i % 2 == 0 else "cpu.large",
                working_dir=f"/path/to/project-{i}",
                num_instances=1 + (i % 5),
                env={"VAR": f"value-{i}"} if i % 3 == 0 else None,
                mounts=[{"local": f"/data{i}", "remote": f"/mnt/data{i}"}] if i % 4 == 0 else None
            )
            configs.append(config)
        
        # Measure validation
        with tracker.measure("task_config_validation"):
            for config in configs:
                # Simulate validation by accessing properties
                _ = config.instance_type
                _ = config.num_instances
                _ = config.env
                _ = config.mounts
    
    def test_large_payload_handling(self):
        """Measure performance with large payloads."""
        # Create task with large environment
        large_env = {f"VAR_{i}": f"value_{i}" * 100 for i in range(100)}
        
        with tracker.measure("large_env_task_creation"):
            task = Task(
                task_id="large-task",
                name="large-task",
                status=TaskStatus.RUNNING,
                created_at="2024-01-01T00:00:00Z",
                instance_type="cpu.large",
                num_instances=1,
                region="us-central1",
                cost_per_hour="$1.00",
                env=large_env
            )
        
        # Measure serialization performance (simulated)
        with tracker.measure("large_env_serialization"):
            import json
            serialized = json.dumps({
                "task_id": task.task_id,
                "env": task.env
            })
            assert len(serialized) > 10000


@pytest.fixture(scope="session", autouse=True)
def performance_report():
    """Generate performance report after all tests."""
    yield
    
    # Generate and print report
    report = tracker.report()
    
    print("\n" + "=" * 80)
    print("PERFORMANCE REGRESSION REPORT")
    print("=" * 80)
    
    for operation, data in sorted(report.items()):
        print(f"\n{operation}:")
        current = data["current"]
        print(f"  Current: {current['duration_ms']:.2f}ms, {current['memory_mb']:.2f}MB")
        
        if "baseline" in data:
            baseline = data["baseline"]
            change = data["change"]
            print(f"  Baseline: {baseline['duration_ms']:.2f}ms, {baseline['memory_mb']:.2f}MB")
            print(f"  Change: {change['duration_pct']:+.1f}% duration, {change['memory_pct']:+.1f}% memory")
            
            # Flag regressions
            if change["duration_pct"] > 20 or change["memory_pct"] > 20:
                print("  ⚠️  REGRESSION DETECTED")
    
    print("\n" + "=" * 80)


def update_baselines():
    """Update performance baselines with current measurements."""
    print("Updating performance baselines...")
    tracker.update_baselines(force=True)
    print(f"Baselines saved to: {tracker.baseline_file}")


if __name__ == "__main__":
    # Run this script directly to update baselines
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--update-baselines":
        # Run tests and update baselines
        pytest.main([__file__, "-v"])
        update_baselines()
    else:
        # Just run tests
        pytest.main([__file__, "-v"])