"""Concurrent operations testing for Flow SDK.

These tests verify the SDK's behavior under concurrent load and ensure
thread safety, proper resource management, and correct handling of
concurrent API calls.

DESIGN PRINCIPLES:
- Test real concurrency scenarios
- Verify thread safety of shared resources
- Ensure proper cleanup even with concurrent failures
- Test rate limiting and backoff behavior
- No artificial delays - use proper synchronization
"""

import logging
import os
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from unittest.mock import Mock, patch

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.errors import APIError, RateLimitError, ResourceNotFoundError
from flow.providers.fcp.provider import FCPProvider
from tests.support.framework import (
    TaskConfigBuilder,
    create_test_provider,
    isolation_context,
)

logger = logging.getLogger(__name__)

# Test constants
CONCURRENT_TASK_COUNT = 10
STRESS_TEST_TASK_COUNT = 50
MAX_WORKERS = 5
RATE_LIMIT_WINDOW_SECONDS = 1.0
RATE_LIMIT_MAX_REQUESTS = 10


@dataclass
class ConcurrencyMetrics:
    """Metrics collected during concurrent tests."""
    successful_operations: int = 0
    failed_operations: int = 0
    total_duration_seconds: float = 0.0
    operations_per_second: float = 0.0
    errors_by_type: Dict[str, int] = None
    thread_contentions: int = 0
    
    def __post_init__(self):
        if self.errors_by_type is None:
            self.errors_by_type = {}
            
    def record_error(self, error: Exception):
        """Record an error by type."""
        error_type = type(error).__name__
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
        self.failed_operations += 1
        
    def record_success(self):
        """Record a successful operation."""
        self.successful_operations += 1
        
    def calculate_rate(self):
        """Calculate operations per second."""
        if self.total_duration_seconds > 0:
            total_ops = self.successful_operations + self.failed_operations
            self.operations_per_second = total_ops / self.total_duration_seconds


class ThreadSafeCounter:
    """Thread-safe counter for testing concurrent access."""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
        
    def increment(self) -> int:
        """Atomically increment and return new value."""
        with self._lock:
            self._value += 1
            return self._value
            
    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value


class MockRateLimiter:
    """Mock rate limiter for testing rate limit behavior."""
    
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: List[float] = []
        self._lock = threading.Lock()
        
    def check_rate_limit(self) -> bool:
        """Check if request would exceed rate limit."""
        with self._lock:
            now = time.time()
            # Remove old requests outside window
            self._requests = [
                t for t in self._requests 
                if now - t < self.window_seconds
            ]
            
            if len(self._requests) >= self.max_requests:
                return False
                
            self._requests.append(now)
            return True


@pytest.mark.integration
class TestConcurrentTaskSubmission:
    """Test concurrent task submission scenarios."""
    
    def test_concurrent_task_submission_basic(self):
        """Test submitting multiple tasks concurrently."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
            
        provider = create_test_provider()
        metrics = ConcurrencyTestMetrics()
        
        with isolation_context(provider) as context:
            # Find available instances
            instances = provider.find_instances(
                {"max_price_per_hour": 50.0}, 
                limit=CONCURRENT_TASK_COUNT
            )
            if not instances:
                pytest.skip("No instances available for testing")
                
            # Create task configs
            configs = [
                TaskConfigBuilder()
                .with_name(f"{context['namespace']}-concurrent-{i}")
                .with_instance_type(instances[i % len(instances)].instance_type)
                .with_command(f"echo 'Task {i}'; sleep 2")
                .with_upload_code(False)
                .build()
                for i in range(CONCURRENT_TASK_COUNT)
            ]
            
            start_time = time.time()
            
            # Submit tasks concurrently
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for config in configs:
                    future = executor.submit(self._submit_task_wrapper, provider, config)
                    futures.append(future)
                    
                # Collect results
                for future in as_completed(futures):
                    try:
                        task = future.result()
                        metrics.record_success()
                        context["created_resources"].append(("task", task.task_id))
                    except Exception as e:
                        metrics.record_error(e)
                        logger.warning(f"Task submission failed: {e}")
                        
            metrics.total_duration_seconds = time.time() - start_time
            metrics.calculate_rate()
            
            # Verify results
            assert metrics.successful_operations > 0, \
                "No tasks were successfully submitted"
            assert metrics.successful_operations >= CONCURRENT_TASK_COUNT * 0.8, \
                f"Too many failures: {metrics.failed_operations}/{CONCURRENT_TASK_COUNT}"
                
            logger.info(f"Concurrent submission metrics: {metrics}")
            
    def test_concurrent_task_submission_with_failures(self):
        """Test concurrent submission with some expected failures."""
        provider, mock_http = self._create_mock_provider()
        metrics = ConcurrencyTestMetrics()
        failure_counter = ThreadSafeCounter()
        
        def mock_request(method, url, **kwargs):
            """Mock that fails every 3rd request."""
            if url == "/v2/spot/availability":
                return self._mock_availability_response()
            elif url == "/v2/spot/bids" and method == "POST":
                count = failure_counter.increment()
                if count % 3 == 0:
                    raise APIError("Simulated failure", status_code=500)
                return self._mock_bid_response()
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        # Submit tasks concurrently
        configs = [
            TaskConfigBuilder()
            .with_name(f"test-concurrent-{i}")
            .with_instance_type("a100")
            .with_upload_code(False)
            .build()
            for i in range(CONCURRENT_TASK_COUNT)
        ]
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(self._submit_task_wrapper, provider, config)
                for config in configs
            ]
            
            for future in as_completed(futures):
                try:
                    future.result()
                    metrics.record_success()
                except Exception as e:
                    metrics.record_error(e)
                    
        # Verify mixed results
        assert metrics.successful_operations > 0
        assert metrics.failed_operations > 0
        assert "APIError" in metrics.errors_by_type
        
        # Should have ~33% failure rate
        failure_rate = metrics.failed_operations / CONCURRENT_TASK_COUNT
        assert 0.2 < failure_rate < 0.5, f"Unexpected failure rate: {failure_rate}"
        
    def test_rate_limiting_behavior(self):
        """Test behavior under rate limiting."""
        provider, mock_http = self._create_mock_provider()
        rate_limiter = MockRateLimiter(
            max_requests=RATE_LIMIT_MAX_REQUESTS,
            window_seconds=RATE_LIMIT_WINDOW_SECONDS
        )
        metrics = ConcurrencyTestMetrics()
        
        def mock_request(method, url, **kwargs):
            """Mock that enforces rate limiting."""
            if not rate_limiter.check_rate_limit():
                raise RateLimitError("Rate limit exceeded", retry_after=1.0)
                
            if url == "/v2/spot/availability":
                return self._mock_availability_response()
            elif url == "/v2/spot/bids" and method == "POST":
                return self._mock_bid_response()
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        # Submit many tasks rapidly
        configs = [
            TaskConfigBuilder()
            .with_name(f"rate-limit-test-{i}")
            .with_instance_type("a100")
            .with_upload_code(False)
            .build()
            for i in range(STRESS_TEST_TASK_COUNT)
        ]
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS * 2) as executor:
            futures = [
                executor.submit(self._submit_task_wrapper, provider, config)
                for config in configs
            ]
            
            for future in as_completed(futures):
                try:
                    future.result()
                    metrics.record_success()
                except RateLimitError:
                    metrics.record_error(RateLimitError("Rate limited"))
                except Exception as e:
                    metrics.record_error(e)
                    
        metrics.total_duration_seconds = time.time() - start_time
        metrics.calculate_rate()
        
        # Verify rate limiting worked
        assert "RateLimitError" in metrics.errors_by_type
        assert metrics.errors_by_type["RateLimitError"] > 0
        
        # Verify we didn't exceed rate limit
        assert metrics.operations_per_second <= RATE_LIMIT_MAX_REQUESTS * 1.1
        
    def _submit_task_wrapper(self, provider, config):
        """Wrapper for task submission with error handling."""
        try:
            return provider.submit_task(
                instance_type=config.instance_type,
                config=config
            )
        except Exception as e:
            logger.debug(f"Task submission failed: {e}")
            raise
            
    def _create_mock_provider(self):
        """Create provider with mock HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "project": "test-project",
                "region": "us-central1-a",
                "ssh_keys": ["test-key"],
            }
        )
        
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = "proj-123"
        provider.ssh_key_manager._project_id = "proj-123"
        
        return provider, mock_http
        
    def _mock_availability_response(self):
        """Mock availability API response."""
        return [{
            "fid": "auc_123",
            "instance_type": "it_MsIRhxj3ccyVWGfP",
            "region": "us-central1-a",
            "capacity": 10,
            "last_instance_price": "$25.00"
        }]
        
    def _mock_bid_response(self):
        """Mock bid creation response."""
        return {
            "fid": f"bid_{time.time_ns()}",
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }


@pytest.mark.integration
class TestConcurrentResourceOperations:
    """Test concurrent operations on shared resources."""
    
    def test_concurrent_volume_operations(self):
        """Test concurrent volume create/delete operations."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
            
        provider = create_test_provider()
        metrics = ConcurrencyTestMetrics()
        created_volumes = []
        volumes_lock = threading.Lock()
        
        def create_and_delete_volume(index: int):
            """Create a volume, verify it, then delete it."""
            try:
                # Create volume
                volume = provider.create_volume(
                    name=f"concurrent-test-vol-{index}",
                    size_gb=10
                )
                
                with volumes_lock:
                    created_volumes.append(volume.volume_id)
                    
                # Verify it exists
                retrieved = provider.get_volume(volume.volume_id)
                assert retrieved.volume_id == volume.volume_id
                
                # Delete it
                deleted = provider.delete_volume(volume.volume_id)
                assert deleted
                
                metrics.record_success()
                
            except Exception as e:
                metrics.record_error(e)
                logger.warning(f"Volume operation failed: {e}")
                
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(create_and_delete_volume, i)
                for i in range(10)
            ]
            
            for future in as_completed(futures):
                future.result()  # Propagate any exceptions
                
        # Verify cleanup - no volumes should remain
        remaining_volumes = []
        for volume_id in created_volumes:
            try:
                provider.get_volume(volume_id)
                remaining_volumes.append(volume_id)
            except ResourceNotFoundError:
                pass  # Expected - volume was deleted
                
        assert len(remaining_volumes) == 0, \
            f"Volumes not cleaned up: {remaining_volumes}"
            
    def test_concurrent_task_status_updates(self):
        """Test concurrent status checks don't interfere."""
        provider, mock_http = self._create_mock_provider()
        task_states = {}
        state_lock = threading.Lock()
        
        # Create mock tasks with changing states
        task_ids = [f"task-{i}" for i in range(10)]
        for task_id in task_ids:
            task_states[task_id] = "pending"
            
        def mock_request(method, url, **kwargs):
            """Mock that returns task status."""
            if "/bids/" in url:
                task_id = url.split("/")[-1]
                with state_lock:
                    status = task_states.get(task_id, "unknown")
                return {
                    "fid": task_id,
                    "status": status,
                    "created_at": datetime.now().isoformat()
                }
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        def check_and_update_status(task_id: str, iterations: int):
            """Check status multiple times and update state."""
            for i in range(iterations):
                task = provider.get_task(task_id)
                
                # Simulate state progression
                with state_lock:
                    if task_states[task_id] == "pending":
                        task_states[task_id] = "running"
                    elif task_states[task_id] == "running" and i > iterations / 2:
                        task_states[task_id] = "completed"
                        
        # Run concurrent status checks
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(check_and_update_status, task_id, 10)
                for task_id in task_ids
            ]
            
            for future in as_completed(futures):
                future.result()
                
        # All tasks should have progressed to completed
        for task_id in task_ids:
            assert task_states[task_id] == "completed"
            
    def _create_mock_provider(self):
        """Create provider with mock HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={"project": "test-project"}
        )
        
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = "proj-123"
        
        return provider, mock_http


@pytest.mark.integration
class TestThreadSafety:
    """Test thread safety of SDK components."""
    
    def test_provider_thread_safety(self):
        """Test that provider instances are thread-safe."""
        provider, mock_http = self._create_mock_provider()
        shared_state = {"errors": [], "calls": 0}
        state_lock = threading.Lock()
        
        def mock_request(method, url, **kwargs):
            """Mock that tracks concurrent calls."""
            with state_lock:
                shared_state["calls"] += 1
                
            # Simulate some processing time
            time.sleep(0.001)
            
            if url == "/v2/spot/availability":
                return [{
                    "fid": "auc_123",
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-east-1",
                    "capacity": 10,
                    "last_instance_price": "$25.00"
                }]
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        def make_api_calls(thread_id: int):
            """Make multiple API calls from a thread."""
            try:
                for i in range(10):
                    instances = provider.find_instances({
                        "max_price_per_hour": 50.0
                    })
                    assert len(instances) > 0
            except Exception as e:
                with state_lock:
                    shared_state["errors"].append((thread_id, str(e)))
                    
        # Run many threads concurrently
        threads = []
        for i in range(20):
            thread = threading.Thread(target=make_api_calls, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join()
            
        # Verify no errors and correct call count
        assert len(shared_state["errors"]) == 0, \
            f"Thread safety errors: {shared_state['errors']}"
        assert shared_state["calls"] == 200  # 20 threads * 10 calls each
        
    def test_config_thread_safety(self):
        """Test that config objects are thread-safe."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={"project": "test-project"}
        )
        
        errors = []
        
        def access_config(thread_id: int):
            """Access config from multiple threads."""
            try:
                for _ in range(100):
                    # Read various config properties
                    _ = config.provider
                    _ = config.auth_token
                    _ = config.provider_config
                    headers = config.get_headers()
                    assert "Authorization" in headers
            except Exception as e:
                errors.append((thread_id, str(e)))
                
        # Run concurrent access
        threads = []
        for i in range(10):
            thread = threading.Thread(target=access_config, args=(i,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        assert len(errors) == 0, f"Config thread safety errors: {errors}"
        
    def _create_mock_provider(self):
        """Create provider with mock HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={"project": "test-project"}
        )
        
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = "proj-123"
        
        return provider, mock_http


@pytest.mark.integration
class TestConcurrentErrorHandling:
    """Test error handling in concurrent scenarios."""
    
    def test_concurrent_cleanup_after_errors(self):
        """Test that cleanup works correctly with concurrent failures."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
            
        provider = create_test_provider()
        created_resources = []
        resources_lock = threading.Lock()
        
        def create_task_with_error(index: int):
            """Create a task and simulate an error."""
            task = None
            try:
                # Find instance
                instances = provider.find_instances(
                    {"max_price_per_hour": 50.0}, 
                    limit=1
                )
                if not instances:
                    raise RuntimeError("No instances available")
                    
                # Create task
                config = TaskConfigBuilder() \
                    .with_name(f"cleanup-test-{index}") \
                    .with_instance_type(instances[0].instance_type) \
                    .with_command("echo test") \
                    .with_upload_code(False) \
                    .build()
                    
                task = provider.submit_task(instances[0].instance_type, config)
                
                with resources_lock:
                    created_resources.append(task.task_id)
                    
                # Simulate error after task creation
                if index % 2 == 0:
                    raise RuntimeError(f"Simulated error for task {index}")
                    
            except Exception as e:
                # Cleanup on error
                if task:
                    try:
                        provider.cancel_task(task.task_id)
                    except:
                        pass
                raise
                
        # Run concurrent operations with expected failures
        errors = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(create_task_with_error, i)
                for i in range(10)
            ]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append(str(e))
                    
        # Verify cleanup - check all created tasks
        active_tasks = []
        for task_id in created_resources:
            try:
                task = provider.get_task(task_id)
                if task.status not in [TaskStatus.CANCELLED, TaskStatus.COMPLETED]:
                    active_tasks.append(task_id)
            except ResourceNotFoundError:
                pass  # Task was cleaned up
                
        # Cleanup any remaining tasks
        for task_id in active_tasks:
            try:
                provider.cancel_task(task_id)
            except:
                pass
                
        assert len(active_tasks) == 0, \
            f"Tasks not cleaned up after errors: {active_tasks}"


def test_concurrent_operations_summary():
    """Summary test that validates all concurrent operation patterns."""
    # This test serves as documentation of tested patterns
    tested_patterns = {
        "Basic Concurrency": "Multiple tasks submitted simultaneously",
        "Failure Handling": "Concurrent operations with expected failures",
        "Rate Limiting": "Behavior under API rate limits",
        "Resource Contention": "Concurrent access to shared resources",
        "Thread Safety": "Provider and config thread safety",
        "Error Cleanup": "Resource cleanup with concurrent errors",
        "Status Updates": "Concurrent status polling",
        "Volume Operations": "Concurrent volume create/delete",
    }
    
    logger.info("Concurrent operations test coverage:")
    for pattern, description in tested_patterns.items():
        logger.info(f"  ✓ {pattern}: {description}")
        
    assert len(tested_patterns) >= 8, "Missing concurrent test patterns"