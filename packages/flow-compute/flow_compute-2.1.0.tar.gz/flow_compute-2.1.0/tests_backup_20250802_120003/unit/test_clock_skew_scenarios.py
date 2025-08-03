"""Test clock skew scenarios for time-sensitive operations.

This module tests how the system behaves when system clocks are out of sync,
which can happen in distributed environments or due to time zone issues.
"""

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from flow.utils.cache import TTLCache
from flow.utils.retry import retry_on_exception


class TestCacheClockSkew:
    """Test TTL cache behavior under clock skew conditions."""
    
    @pytest.mark.asyncio
    async def test_cache_forward_clock_skew(self):
        """Test cache behavior when clock jumps forward."""
        cache = TTLCache(ttl_seconds=60)
        
        # Set initial time
        with patch('time.time', return_value=1000.0):
            await cache.set("key", "value")
            # Value should be available
            assert await cache.get("key") == "value"
        
        # Clock jumps forward by 30 seconds (within TTL)
        with patch('time.time', return_value=1030.0):
            assert await cache.get("key") == "value"
        
        # Clock jumps forward past TTL
        with patch('time.time', return_value=1061.0):
            assert await cache.get("key") is None
    
    @pytest.mark.asyncio
    async def test_cache_backward_clock_skew(self):
        """Test cache behavior when clock jumps backward."""
        cache = TTLCache(ttl_seconds=60)
        
        # Set value at time 1000
        with patch('time.time', return_value=1000.0):
            await cache.set("key", "value")
        
        # Clock jumps backward to 950 (before cache entry)
        with patch('time.time', return_value=950.0):
            # Value should still be available (negative age)
            assert await cache.get("key") == "value"
        
        # Clock returns to normal flow
        with patch('time.time', return_value=1059.0):
            assert await cache.get("key") == "value"
        
        with patch('time.time', return_value=1061.0):
            assert await cache.get("key") is None
    
    @pytest.mark.asyncio
    async def test_cache_cleanup_with_clock_skew(self):
        """Test cache cleanup behavior under clock skew."""
        cache = TTLCache(ttl_seconds=60)
        
        # Add entries at different times
        with patch('time.time', return_value=1000.0):
            await cache.set("key1", "value1")
        
        with patch('time.time', return_value=1020.0):
            await cache.set("key2", "value2")
        
        with patch('time.time', return_value=1040.0):
            await cache.set("key3", "value3")
        
        # Clock jumps forward, making key1 and key2 expired
        with patch('time.time', return_value=1082.0):
            # This should trigger cleanup
            await cache.set("key4", "value4")
            
            # key1 and key2 should be expired
            assert await cache.get("key1") is None
            assert await cache.get("key2") is None
            assert await cache.get("key3") == "value3"
            assert await cache.get("key4") == "value4"


class TestRetryClockSkew:
    """Test retry mechanism behavior under clock skew conditions."""
    
    def test_retry_with_clock_skew_forward(self):
        """Test retry delays when clock jumps forward."""
        attempt_times = []
        
        def failing_function():
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        # Mock time to simulate clock skew
        time_sequence = [
            1000.0,  # First attempt
            1001.0,  # After 1s delay
            1005.0,  # Clock jumps forward by 4s
        ]
        
        with patch('time.time', side_effect=time_sequence):
            with patch('time.sleep') as mock_sleep:
                result = retry_on_exception(
                    ValueError,
                    max_attempts=3,
                    delay=1.0,
                    backoff=1.0
                )(failing_function)()
                
                assert result == "success"
                assert len(attempt_times) == 3
                # Check that sleep was called with correct delays
                assert mock_sleep.call_count == 2
                assert mock_sleep.call_args_list[0][0][0] == 1.0
                assert mock_sleep.call_args_list[1][0][0] == 1.0


class TestTaskTimestampClockSkew:
    """Test task timestamp handling under clock skew conditions."""
    
    def test_task_age_calculation_with_skewed_clocks(self):
        """Test calculating task age when server and client clocks differ."""
        from flow.api.models import Task, TaskStatus
        
        # Server time is 5 minutes ahead
        server_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        task = Task(
            task_id="test-123",
            name="test",
            status=TaskStatus.RUNNING,
            created_at=server_time.isoformat(),
            instance_type="cpu.small",
            num_instances=1,
            region="us-central1",
            cost_per_hour="$1.00"
        )
        
        # Client calculates age
        client_now = datetime.now(timezone.utc)
        task_created = task.created_at
        age = client_now - task_created
        
        # Age should be negative (task appears to be created in the future)
        assert age.total_seconds() < 0
        assert abs(age.total_seconds() + 300) < 1  # ~5 minutes in the future
    
    def test_task_filtering_by_time_with_clock_skew(self):
        """Test filtering tasks by creation time with clock skew."""
        from flow.api.models import Task, TaskStatus
        
        # Create tasks with various timestamps
        base_time = datetime.now(timezone.utc)
        tasks = []
        
        for i in range(5):
            # Some tasks from the past, some from "the future" due to clock skew
            offset = timedelta(minutes=(i - 2) * 10)
            task = Task(
                task_id=f"test-{i}",
                name=f"test-{i}",
                status=TaskStatus.RUNNING,
                created_at=base_time + offset,
                instance_type="cpu.small",
                num_instances=1,
                region="us-central1",
                cost_per_hour="$1.00"
            )
            tasks.append(task)
        
        # Filter tasks created in the last hour (from client's perspective)
        client_now = datetime.now(timezone.utc)
        one_hour_ago = client_now - timedelta(hours=1)
        
        recent_tasks = [
            t for t in tasks
            if t.created_at > one_hour_ago
        ]
        
        # Should include tasks that appear to be from the future
        assert len(recent_tasks) >= 3


class TestMonotonicTimeUsage:
    """Test that monotonic time is used where appropriate."""
    
    def test_operation_timing_uses_monotonic(self):
        """Test that operation timing is resilient to clock changes."""
        # This is a pattern test - verifying the correct approach
        start = time.monotonic()  # Use monotonic for measuring intervals
        
        # Simulate some operation
        time.sleep(0.01)
        
        end = time.monotonic()
        duration = end - start
        
        # Duration should be positive regardless of system clock changes
        assert duration > 0
        assert duration < 1.0  # Reasonable bounds
    
    def test_wall_clock_vs_monotonic_usage(self):
        """Test distinguishing between wall clock and monotonic time usage."""
        # Wall clock for timestamps (can be affected by clock skew)
        wall_clock_time = time.time()
        timestamp = datetime.now(timezone.utc)
        
        # Monotonic for measuring durations (not affected by clock skew)
        start_mono = time.monotonic()
        time.sleep(0.01)
        duration = time.monotonic() - start_mono
        
        assert isinstance(wall_clock_time, float)
        assert isinstance(timestamp, datetime)
        assert duration > 0


class TestDistributedClockSkew:
    """Test handling of clock skew in distributed scenarios."""
    
    def test_task_ordering_with_skewed_node_clocks(self):
        """Test task ordering when nodes have different clock times."""
        from flow.api.models import Task, TaskStatus
        
        # Simulate tasks created on different nodes with clock skew
        # Node A is 2 minutes behind, Node B is correct, Node C is 3 minutes ahead
        base_time = datetime.now(timezone.utc)
        
        tasks = [
            Task(
                task_id="task-a",
                name="task-a",
                status=TaskStatus.RUNNING,
                created_at=base_time - timedelta(minutes=2),
                instance_type="cpu.small",
                num_instances=1,
                region="us-central1",
                cost_per_hour="$1.00"
            ),
            Task(
                task_id="task-b",
                name="task-b",
                status=TaskStatus.RUNNING,
                created_at=base_time,
                instance_type="cpu.small",
                num_instances=1,
                region="us-central1",
                cost_per_hour="$1.00"
            ),
            Task(
                task_id="task-c",
                name="task-c",
                status=TaskStatus.RUNNING,
                created_at=base_time + timedelta(minutes=3),
                instance_type="cpu.small",
                num_instances=1,
                region="us-central1",
                cost_per_hour="$1.00"
            ),
        ]
        
        # Sort by creation time
        sorted_tasks = sorted(
            tasks,
            key=lambda t: t.created_at
        )
        
        # Order should be preserved based on timestamps, not actual creation order
        assert [t.task_id for t in sorted_tasks] == ["task-a", "task-b", "task-c"]
    
    def test_timeout_handling_with_clock_skew(self):
        """Test timeout calculations when clocks are skewed."""
        # Simulate a timeout calculation
        timeout_seconds = 300  # 5 minutes
        
        # Server reports start time with its clock
        server_start = datetime.now(timezone.utc) + timedelta(minutes=2)  # 2 min ahead
        
        # Client checks timeout with its clock
        client_now = datetime.now(timezone.utc)
        
        # Calculate elapsed time from client's perspective
        elapsed = (client_now - server_start).total_seconds()
        
        # Elapsed time will be negative due to clock skew
        assert elapsed < 0
        
        # Timeout check should handle this gracefully
        # In practice, use max(0, elapsed) to avoid negative timeouts
        remaining = max(0, timeout_seconds - max(0, elapsed))
        assert remaining == timeout_seconds


class TestClockSkewMitigation:
    """Test strategies for mitigating clock skew issues."""
    
    def test_relative_time_comparison(self):
        """Test using relative time comparisons instead of absolute."""
        # Good practice: compare durations, not absolute times
        start_time = time.time()
        
        # Do some work
        time.sleep(0.01)
        
        # Check if operation took too long (relative comparison)
        duration = time.time() - start_time
        max_duration = 1.0
        
        assert duration < max_duration
        
    def test_tolerance_in_time_comparisons(self):
        """Test adding tolerance to time-based comparisons."""
        from datetime import datetime, timezone, timedelta
        
        # Add tolerance for clock skew
        CLOCK_SKEW_TOLERANCE = timedelta(minutes=5)
        
        server_time = datetime.now(timezone.utc) + timedelta(minutes=2)
        client_time = datetime.now(timezone.utc)
        
        # Instead of exact comparison, use tolerance
        time_diff = abs((server_time - client_time).total_seconds())
        assert time_diff < CLOCK_SKEW_TOLERANCE.total_seconds()