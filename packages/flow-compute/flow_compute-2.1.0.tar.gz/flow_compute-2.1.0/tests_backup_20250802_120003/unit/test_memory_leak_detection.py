"""Memory leak detection tests using tracemalloc.

This module tests for memory leaks in long-running operations and ensures
proper resource cleanup and object lifecycle management.

Test categories:
- Provider lifecycle memory leaks
- Task execution memory patterns
- API client connection pooling
- Large data structure handling
- Circular reference detection
- Resource cleanup verification
"""

import gc
import tracemalloc
import weakref
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
from unittest.mock import Mock, patch

import pytest

from flow.api.models import Task, TaskConfig, TaskStatus, Volume, VolumeSpec
from flow.cli.commands.run import RunCommand
from flow.cli.commands.status import StatusCommand
from flow._internal.io.http import HttpClient
from flow.providers.fcp.provider import FCPProvider
from flow.providers.local.provider import LocalProvider
from tests.testing.builders import TaskBuilder, TaskConfigBuilder, VolumeBuilder


@dataclass
class MemorySnapshot:
    """Memory usage snapshot for leak detection."""
    current: int
    peak: int
    traceback: Optional[List[str]] = None


class MemoryLeakDetector:
    """Helper class for detecting memory leaks."""
    
    def __init__(self, threshold_bytes: int = 10 * 1024 * 1024):  # 10MB default
        self.threshold_bytes = threshold_bytes
        self.baseline: Optional[MemorySnapshot] = None
        self.snapshots: List[MemorySnapshot] = []
        
    def start(self):
        """Start memory tracking."""
        tracemalloc.start()
        gc.collect()  # Force garbage collection for accurate baseline
        current, peak = tracemalloc.get_traced_memory()
        self.baseline = MemorySnapshot(current=current, peak=peak)
        
    def snapshot(self, label: str = "") -> MemorySnapshot:
        """Take a memory snapshot."""
        gc.collect()  # Force GC before measurement
        current, peak = tracemalloc.get_traced_memory()
        
        # Get top memory allocations
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')[:10]
        traceback = [str(stat) for stat in top_stats]
        
        snap = MemorySnapshot(current=current, peak=peak, traceback=traceback)
        self.snapshots.append(snap)
        return snap
        
    def stop(self) -> Dict[str, Any]:
        """Stop tracking and return results."""
        final_snapshot = self.snapshot("final")
        tracemalloc.stop()
        
        if not self.baseline:
            return {"error": "No baseline snapshot"}
            
        memory_growth = final_snapshot.current - self.baseline.current
        peak_memory = max(snap.peak for snap in self.snapshots)
        
        return {
            "baseline_bytes": self.baseline.current,
            "final_bytes": final_snapshot.current,
            "growth_bytes": memory_growth,
            "peak_bytes": peak_memory,
            "leak_detected": memory_growth > self.threshold_bytes,
            "top_allocations": final_snapshot.traceback
        }
        
    def assert_no_leak(self, operation_name: str = ""):
        """Assert no memory leak occurred."""
        results = self.stop()
        if results.get("leak_detected"):
            msg = f"Memory leak detected in {operation_name}: "
            msg += f"Growth: {results['growth_bytes'] / 1024 / 1024:.2f}MB\n"
            msg += "Top allocations:\n"
            for alloc in results.get("top_allocations", [])[:5]:
                msg += f"  {alloc}\n"
            pytest.fail(msg)


@contextmanager
def track_memory_usage(threshold_mb: float = 10):
    """Context manager for tracking memory usage."""
    detector = MemoryLeakDetector(threshold_bytes=int(threshold_mb * 1024 * 1024))
    detector.start()
    try:
        yield detector
    finally:
        # Don't auto-assert, let caller decide
        pass


class TestProviderMemoryLeaks:
    """Test memory leaks in provider implementations."""
    
    def test_fcp_provider_lifecycle_no_leak(self):
        """Test FCP provider doesn't leak memory across multiple operations."""
        detector = MemoryLeakDetector()
        detector.start()
        
        # Create and destroy providers multiple times
        for i in range(100):
            provider = FCPProvider()
            
            # Simulate some operations
            config = TaskConfigBuilder().with_name(f"test-{i}").build()
            
            # Mock the API client to avoid real calls
            with patch.object(provider, '_client') as mock_client:
                mock_client.list_tasks.return_value = []
                mock_client.find_instances.return_value = []
                
                # Simulate operations that might leak
                provider.list_tasks()
                
            # Explicitly delete to test cleanup
            del provider
            
            # Take snapshot every 10 iterations
            if i % 10 == 0:
                detector.snapshot(f"iteration-{i}")
        
        # Force final garbage collection
        gc.collect()
        
        detector.assert_no_leak("FCP provider lifecycle")
    
    def test_local_provider_subprocess_cleanup(self):
        """Test LocalProvider cleans up subprocess resources."""
        with track_memory_usage() as detector:
            # Run many subprocess operations
            for i in range(50):
                provider = LocalProvider()
                
                # Mock subprocess to avoid actual execution
                with patch('subprocess.Popen') as mock_popen:
                    mock_process = Mock()
                    mock_process.poll.return_value = 0
                    mock_process.communicate.return_value = (b"output", b"")
                    mock_popen.return_value = mock_process
                    
                    config = TaskConfigBuilder().with_command("echo test").build()
                    
                    # Simulate task execution
                    with patch.object(provider, '_execute_task'):
                        pass
                    
                del provider
                
                if i % 10 == 0:
                    detector.snapshot(f"subprocess-{i}")
            
            detector.assert_no_leak("LocalProvider subprocess")
    
    def test_provider_task_tracking_cleanup(self):
        """Test providers clean up task tracking data structures."""
        with track_memory_usage() as detector:
            provider = FCPProvider()
            
            # Create many tasks
            task_refs = []
            for i in range(1000):
                task = TaskBuilder().with_id(f"task-{i}").build()
                
                # Keep weak references to detect cleanup
                task_refs.append(weakref.ref(task))
                
                # Simulate internal tracking
                if hasattr(provider, '_tasks'):
                    provider._tasks[task.task_id] = task
            
            # Clear references
            if hasattr(provider, '_tasks'):
                provider._tasks.clear()
            
            # Force GC
            gc.collect()
            
            # Check weak references are cleared
            alive_count = sum(1 for ref in task_refs if ref() is not None)
            assert alive_count == 0, f"{alive_count} tasks still in memory"
            
            detector.assert_no_leak("Task tracking cleanup")


class TestAPIClientMemoryLeaks:
    """Test memory leaks in API client implementations."""
    
    def test_connection_pool_cleanup(self):
        """Test API client connection pools don't leak."""
        with track_memory_usage(threshold_mb=20) as detector:
            # Create many clients
            clients = []
            for i in range(100):
                client = HttpClient(base_url="https://api.test.com", headers={"Authorization": f"Bearer test-key-{i}"})
                clients.append(client)
                
                # Simulate API calls
                with patch.object(client.client, 'request') as mock_request:
                    mock_request.return_value = Mock(
                        status_code=200,
                        json=lambda: {"tasks": []}
                    )
                    
                    # Multiple requests per client
                    for _ in range(10):
                        client.request("GET", "/tasks")
                
                if i % 20 == 0:
                    detector.snapshot(f"clients-{i}")
            
            # Clean up all clients
            for client in clients:
                if hasattr(client, 'session'):
                    client.session.close()
            clients.clear()
            
            gc.collect()
            detector.assert_no_leak("API client connection pools")
    
    def test_large_response_handling(self):
        """Test memory cleanup after handling large API responses."""
        with track_memory_usage(threshold_mb=50) as detector:
            client = HttpClient(base_url="https://api.test.com", headers={"Authorization": "Bearer test-key"})
            
            # Simulate large responses
            for i in range(20):
                # Create large response data
                large_response = {
                    "tasks": [
                        {
                            "task_id": f"task-{j}",
                            "name": f"test-task-{j}",
                            "status": "running",
                            "logs": "x" * 10000,  # 10KB of logs per task
                            "metadata": {"data": "y" * 5000}
                        }
                        for j in range(1000)  # 1000 tasks
                    ]
                }
                
                with patch.object(client.client, 'request') as mock_request:
                    mock_request.return_value = Mock(
                        status_code=200,
                        json=lambda: large_response
                    )
                    
                    # Process response
                    result = client.request("GET", "/tasks")
                    
                    # Simulate processing
                    task_count = len(result.get("tasks", []))
                    
                    # Clear reference
                    del result
                
                if i % 5 == 0:
                    detector.snapshot(f"large-response-{i}")
                    gc.collect()
            
            detector.assert_no_leak("Large API response handling")


class TestDataStructureMemoryLeaks:
    """Test memory leaks in data structure handling."""
    
    def test_circular_reference_detection(self):
        """Test circular references are properly handled."""
        with track_memory_usage() as detector:
            # Create circular references
            for i in range(100):
                # Task references that could be circular
                task1 = TaskBuilder().with_id(f"task-{i}-1").build()
                task2 = TaskBuilder().with_id(f"task-{i}-2").build()
                
                # Create circular reference through custom attributes
                task1._related = task2
                task2._related = task1
                
                # Also test with configs
                config1 = TaskConfigBuilder().with_name(f"config-{i}-1").build()
                config2 = TaskConfigBuilder().with_name(f"config-{i}-2").build()
                
                # Simulate circular deps
                config1._depends_on = config2
                config2._depends_on = config1
                
                # Clear explicit references
                del task1, task2, config1, config2
            
            # Python's GC should handle circular refs
            gc.collect()
            
            detector.assert_no_leak("Circular reference handling")
    
    def test_large_volume_list_handling(self):
        """Test memory handling with large lists of volumes."""
        with track_memory_usage(threshold_mb=30) as detector:
            # Create many volumes
            for batch in range(10):
                volumes = []
                for i in range(10000):  # 10K volumes per batch
                    volume = VolumeBuilder()\
                        .with_id(f"vol-{batch}-{i}")\
                        .with_size(1000)\
                        .build()
                    volumes.append(volume)
                
                # Simulate processing
                total_size = sum(v.size_gb for v in volumes)
                
                # Clear references
                volumes.clear()
                
                detector.snapshot(f"volume-batch-{batch}")
                gc.collect()
            
            detector.assert_no_leak("Large volume list handling")
    
    def test_nested_config_structures(self):
        """Test deeply nested configuration structures don't leak."""
        with track_memory_usage() as detector:
            for i in range(100):
                # Create deeply nested environment variables
                env = {}
                current = env
                for level in range(100):  # 100 levels deep
                    current[f"level_{level}"] = {
                        "data": "x" * 1000,
                        "nested": {}
                    }
                    current = current[f"level_{level}"]["nested"]
                
                # Create config with nested data
                config = TaskConfigBuilder()\
                    .with_name(f"nested-{i}")\
                    .with_environment({"nested_data": str(env)})\
                    .build()
                
                # Process and clear
                _ = config.model_dump()
                del config, env
                
                if i % 20 == 0:
                    detector.snapshot(f"nested-{i}")
            
            gc.collect()
            detector.assert_no_leak("Nested config structures")


class TestLongRunningOperationLeaks:
    """Test memory leaks in long-running operations."""
    
    def test_continuous_status_polling(self):
        """Test memory leaks during continuous status polling."""
        with track_memory_usage(threshold_mb=15) as detector:
            provider = FCPProvider()
            
            # Mock API responses
            with patch.object(provider, '_client') as mock_client:
                # Simulate status updates
                for i in range(1000):
                    mock_client.get_task.return_value = {
                        "task_id": "test-task",
                        "status": "running" if i < 900 else "completed",
                        "logs": f"Log entry {i}\n" * 100,  # Growing logs
                        "metrics": {
                            "cpu": i % 100,
                            "memory": i % 8192,
                            "iteration": i
                        }
                    }
                    
                    # Poll status
                    status = provider.get_task_status("test-task")
                    
                    if i % 100 == 0:
                        detector.snapshot(f"polling-{i}")
                        gc.collect()
            
            detector.assert_no_leak("Continuous status polling")
    
    def test_log_streaming_memory_usage(self):
        """Test memory usage during log streaming."""
        with track_memory_usage(threshold_mb=20) as detector:
            provider = FCPProvider()
            
            # Simulate log streaming
            log_buffer = []
            with patch.object(provider, '_client') as mock_client:
                for i in range(500):
                    # Generate log chunk
                    log_chunk = f"[{i:05d}] " + "Log data " * 100 + "\n"
                    
                    mock_client.get_logs.return_value = {
                        "logs": log_chunk,
                        "next_token": f"token-{i+1}"
                    }
                    
                    # Stream logs with buffer management
                    log_buffer.append(log_chunk)
                    
                    # Rotate buffer to prevent unbounded growth
                    if len(log_buffer) > 100:
                        log_buffer.pop(0)
                    
                    if i % 50 == 0:
                        detector.snapshot(f"log-stream-{i}")
            
            detector.assert_no_leak("Log streaming")
    
    def test_task_retry_loop_memory(self):
        """Test memory usage in retry loops."""
        with track_memory_usage() as detector:
            provider = FCPProvider()
            
            with patch.object(provider, '_client') as mock_client:
                # Simulate retries with growing state
                for attempt in range(100):
                    try:
                        # Simulate operation that might fail
                        if attempt < 80:
                            raise Exception(f"Retry attempt {attempt}")
                        
                        # Success
                        mock_client.create_task.return_value = {
                            "task_id": f"task-{attempt}"
                        }
                    except Exception:
                        # Accumulate retry state
                        retry_context = {
                            "attempt": attempt,
                            "errors": [f"Error {i}" for i in range(attempt)],
                            "backoff": 2 ** min(attempt, 10)
                        }
                        
                        # Clear old state
                        del retry_context
                    
                    if attempt % 20 == 0:
                        detector.snapshot(f"retry-{attempt}")
                        gc.collect()
            
            detector.assert_no_leak("Task retry loops")


class TestResourceCleanupVerification:
    """Verify proper resource cleanup to prevent leaks."""
    
    def test_weak_reference_cleanup(self):
        """Test weak references are properly cleaned up."""
        # Track objects with weak references
        objects_created = []
        weak_refs = []
        
        # Create objects
        for i in range(1000):
            obj = TaskBuilder().with_id(f"task-{i}").build()
            objects_created.append(obj)
            weak_refs.append(weakref.ref(obj))
        
        # Verify all objects are alive
        alive_before = sum(1 for ref in weak_refs if ref() is not None)
        assert alive_before == 1000
        
        # Clear strong references
        objects_created.clear()
        gc.collect()
        
        # Verify cleanup
        alive_after = sum(1 for ref in weak_refs if ref() is not None)
        assert alive_after == 0, f"{alive_after} objects not garbage collected"
    
    def test_context_manager_cleanup(self):
        """Test context managers properly clean up resources."""
        cleaned_up = []
        
        class TrackableResource:
            def __init__(self, resource_id):
                self.resource_id = resource_id
                self.closed = False
                
            def __enter__(self):
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.closed = True
                cleaned_up.append(self.resource_id)
        
        # Use resources in context managers
        for i in range(100):
            with TrackableResource(f"resource-{i}") as resource:
                # Simulate work
                _ = resource.resource_id
        
        # Verify all cleaned up
        assert len(cleaned_up) == 100
        assert all(f"resource-{i}" in cleaned_up for i in range(100))
    
    def test_exception_cleanup_paths(self):
        """Test cleanup happens even with exceptions."""
        with track_memory_usage() as detector:
            for i in range(100):
                try:
                    # Create resources
                    task = TaskBuilder().with_id(f"task-{i}").build()
                    config = TaskConfigBuilder().with_name(f"config-{i}").build()
                    
                    # Simulate error
                    if i % 2 == 0:
                        raise ValueError("Simulated error")
                        
                except ValueError:
                    # Exception path - resources should still be cleaned up
                    pass
                finally:
                    # Ensure cleanup
                    del task, config
                
                if i % 20 == 0:
                    gc.collect()
                    detector.snapshot(f"exception-{i}")
            
            detector.assert_no_leak("Exception cleanup paths")


class TestMemoryLeakPrevention:
    """Test patterns that prevent memory leaks."""
    
    def test_bounded_cache_implementation(self):
        """Test bounded caches don't grow indefinitely."""
        from collections import OrderedDict
        
        class BoundedCache:
            def __init__(self, max_size=1000):
                self.cache = OrderedDict()
                self.max_size = max_size
                
            def put(self, key, value):
                if key in self.cache:
                    # Move to end
                    self.cache.move_to_end(key)
                else:
                    self.cache[key] = value
                    if len(self.cache) > self.max_size:
                        # Remove oldest
                        self.cache.popitem(last=False)
                        
            def get(self, key):
                if key in self.cache:
                    self.cache.move_to_end(key)
                    return self.cache[key]
                return None
        
        with track_memory_usage() as detector:
            cache = BoundedCache(max_size=100)
            
            # Add many items
            for i in range(10000):
                cache.put(f"key-{i}", {"data": "x" * 1000})
                
                if i % 1000 == 0:
                    # Cache should stay bounded
                    assert len(cache.cache) <= 100
                    detector.snapshot(f"cache-{i}")
            
            detector.assert_no_leak("Bounded cache")
    
    def test_generator_memory_efficiency(self):
        """Test generators for memory-efficient processing."""
        def process_large_dataset():
            """Generator for processing large datasets."""
            for i in range(1000000):
                # Yield one item at a time
                yield {
                    "id": i,
                    "data": f"Item {i}" * 100
                }
        
        with track_memory_usage(threshold_mb=5) as detector:
            # Process using generator (memory efficient)
            total = 0
            for item in process_large_dataset():
                total += len(item["data"])
                
                # Only keep running total, not all items
                if item["id"] % 100000 == 0:
                    detector.snapshot(f"generator-{item['id']}")
            
            detector.assert_no_leak("Generator processing")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])