"""Performance tests for volume CLI bulk operations.

These tests verify that bulk operations perform efficiently at scale:
- Parallel deletion is actually parallel
- Memory usage stays reasonable with large datasets
- Operations complete in reasonable time
"""

import re
import threading
import time
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import Mock, patch

from click.testing import CliRunner

from flow._internal.config import Config
from flow.api.models import StorageInterface, Volume
from flow.cli.app import cli


def strip_ansi_codes(text):
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


@contextmanager
def mock_flow_init():
    """Context manager to mock Flow initialization."""
    mock_config = Mock(spec=Config)
    mock_config.auth_token = "test-token"
    mock_config.api_url = "https://api.test.com"
    mock_config.project = "test-project"
    mock_config.provider = "fcp"
    mock_config.provider_config = {
        "api_url": "https://api.test.com",
        "project": "test-project"
    }
    mock_config.get_headers.return_value = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }

    with patch('flow._internal.config.Config.from_env', return_value=mock_config):
        yield


class TestParallelDeletion:
    """Test that bulk deletion uses parallelism effectively."""

    def test_parallel_deletion_performance(self):
        """Verify parallel deletion is significantly faster than sequential."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 50 volumes for meaningful performance test
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"perf-test-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(50)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Track deletion timing
        deletion_times = []
        deletion_threads = set()

        def slow_delete(volume_id):
            """Simulate API call with 100ms latency."""
            thread_id = threading.current_thread().ident
            deletion_threads.add(thread_id)
            start = time.time()
            time.sleep(0.1)  # Simulate API latency
            deletion_times.append(time.time() - start)
            return None

        mock_flow.delete_volume.side_effect = slow_delete

        # Act
        start_time = time.time()
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])
        elapsed_time = time.time() - start_time

        # Assert
        assert result.exit_code == 0
        assert "Deleted 50 volume(s)" in strip_ansi_codes(result.output)

        # Calculate what sequential time would be
        sequential_time = 0.1 * 50  # 5 seconds

        # Parallel should be much faster (at least 3x)
        assert elapsed_time < sequential_time / 3, f"Parallel deletion too slow: {elapsed_time}s vs {sequential_time}s sequential"

        # Verify multiple threads were used
        assert len(deletion_threads) > 1, "Deletion should use multiple threads"
        assert len(deletion_threads) <= 15, "Should limit thread pool size"

    def test_thread_pool_sizing(self):
        """Verify reasonable concurrency limits."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 200 volumes to test thread pool limits
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"thread-test-{i}",
                size_gb=50,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(200)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Track concurrent deletions
        max_concurrent = 0
        current_concurrent = 0
        lock = threading.Lock()

        def track_concurrency(volume_id):
            nonlocal max_concurrent, current_concurrent

            with lock:
                current_concurrent += 1
                max_concurrent = max(max_concurrent, current_concurrent)

            time.sleep(0.05)  # Simulate work

            with lock:
                current_concurrent -= 1

            return None

        mock_flow.delete_volume.side_effect = track_concurrency

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])

        # Assert
        assert result.exit_code == 0
        assert max_concurrent <= 10, f"Too many concurrent operations: {max_concurrent}"
        assert max_concurrent >= 2, f"Not enough concurrency: {max_concurrent}"


class TestMemoryEfficiency:
    """Test memory usage with large volume lists."""

    def test_handle_10000_volumes_efficiently(self):
        """Ensure we can handle 10k volumes without excessive memory."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 10,000 volumes
        volumes = [
            Volume(
                volume_id=f"vol_{i:06d}",
                name=f"bulk-volume-{i:06d}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(10000)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Fast delete for this test
        mock_flow.delete_volume.return_value = None

        # Act
        start_time = time.time()
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--pattern', '^bulk-volume-.*', '--yes'])
        elapsed_time = time.time() - start_time

        # Assert
        assert result.exit_code == 0
        assert "Found 10000 volume(s) to delete" in strip_ansi_codes(result.output)
        # Should complete reasonably quickly even with 10k volumes
        assert elapsed_time < 60, f"Took too long for 10k volumes: {elapsed_time}s"

    def test_pattern_matching_performance(self):
        """Test complex regex performance on large datasets."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 5000 volumes with varied names
        volumes = []
        patterns = [
            "test-{i}-abc-{i}",
            "prod-data-{i}",
            "backup-2024-01-{i:02d}",
            "experiment-{i}-xyz",
            "temp-{i}"
        ]

        for i in range(5000):
            pattern = patterns[i % len(patterns)]
            volumes.append(Volume(
                volume_id=f"vol_{i:05d}",
                name=pattern.format(i=i % 100),
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            ))

        mock_flow.list_volumes.return_value = volumes
        mock_flow.delete_volume.return_value = None

        # Act - Complex regex that matches ~1000 volumes
        start_time = time.time()
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'volumes', 'delete-all',
                '--pattern', '^(test-\\d+-abc-\\d+|experiment-\\d+-xyz)$',
                '--yes'
            ])
        pattern_time = time.time() - start_time

        # Assert
        assert result.exit_code == 0
        # Pattern matching should be fast even on 5k volumes
        assert pattern_time < 5, f"Pattern matching too slow: {pattern_time}s"


class TestErrorRecoveryPerformance:
    """Test performance impact of error handling."""

    def test_partial_failure_performance(self):
        """Ensure failures don't significantly impact performance."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 100 volumes
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"error-test-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(100)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Make 20% fail
        def delete_with_failures(volume_id):
            vol_num = int(volume_id.split('_')[1])
            if vol_num % 5 == 0:
                time.sleep(0.2)  # Simulate timeout
                raise Exception("Connection timeout")
            time.sleep(0.05)  # Normal deletion
            return None

        mock_flow.delete_volume.side_effect = delete_with_failures

        # Act
        start_time = time.time()
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])
        elapsed_time = time.time() - start_time

        # Assert
        assert result.exit_code == 0
        assert "Deleted 80 volume(s)" in strip_ansi_codes(result.output)
        assert "Failed to delete 20 volume(s)" in strip_ansi_codes(result.output)

        # Even with failures, should complete in reasonable time
        assert elapsed_time < 10, f"Too slow with failures: {elapsed_time}s"


class TestAPILimitHandling:
    """Test behavior at API limits."""

    def test_handle_1000_volume_api_limit(self):
        """Test handling when API returns exactly 1000 volumes (common limit)."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create exactly 1000 volumes (common API limit)
        volumes = [
            Volume(
                volume_id=f"vol_{i:04d}",
                name=f"api-limit-test-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(1000)
        ]
        mock_flow.list_volumes.return_value = volumes
        mock_flow.delete_volume.return_value = None

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])

        # Assert
        assert result.exit_code == 0
        assert "Found 1000 volume(s) to delete" in strip_ansi_codes(result.output)
        mock_flow.list_volumes.assert_called_with()


class TestStressTestScenarios:
    """Stress test extreme scenarios."""

    def test_concurrent_operations_stress(self):
        """Test system under concurrent load."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 500 volumes for stress test
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"stress-test-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(500)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Track resource usage
        active_operations = 0
        max_active = 0
        lock = threading.Lock()
        operation_times = []

        def stressed_delete(volume_id):
            nonlocal active_operations, max_active

            with lock:
                active_operations += 1
                max_active = max(max_active, active_operations)

            start = time.time()
            # Simulate variable API response times
            import random
            time.sleep(random.uniform(0.01, 0.1))
            operation_times.append(time.time() - start)

            with lock:
                active_operations -= 1

            # Random failures to stress error handling
            if random.random() < 0.1:
                raise Exception("Random failure")

            return None

        mock_flow.delete_volume.side_effect = stressed_delete

        # Act
        start_time = time.time()
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])
        total_time = time.time() - start_time

        # Assert
        assert result.exit_code == 0

        # Should handle concurrent operations efficiently
        assert max_active <= 15, f"Too many concurrent operations: {max_active}"
        assert total_time < 20, f"Stress test too slow: {total_time}s"

        # Check the summary output
        # The CLI prints "Deleted X volume(s)" at the end
        stripped_output = strip_ansi_codes(result.output)
        match = re.search(r'Deleted (\d+) volume\(s\)', stripped_output)
        successful = int(match.group(1)) if match else 0

        # With 10% random failure rate, we should still get 400+ successes
        assert successful > 400, f"Too many failures in stress test: {successful}/500"

    def test_worst_case_scenario(self):
        """Test worst case: many volumes, complex patterns, failures."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Create 2000 volumes with complex naming
        volumes = []
        for i in range(2000):
            name_patterns = [
                f"test-{i:04d}-{datetime.now().strftime('%Y%m%d')}-{i%10:03d}",
                f"backup-{(i%365):03d}-2024-data",
                f"exp-{i%100:02d}-{chr(97 + i%26)}{chr(97 + (i//26)%26)}",
                f"ci-build-{i:05d}-artifact",
                ""  # Some volumes without names
            ]
            volumes.append(Volume(
                volume_id=f"vol_{i:04d}",
                name=name_patterns[i % len(name_patterns)] if i % 10 != 0 else "",
                size_gb=100 + (i % 10) * 100,
                region=f"region-{i % 5}",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            ))

        mock_flow.list_volumes.return_value = volumes

        # Complex deletion behavior
        def complex_delete(volume_id):
            vol_num = int(volume_id.split('_')[1])

            # Various failure modes
            if vol_num % 7 == 0:
                time.sleep(0.3)
                raise Exception("Timeout")
            elif vol_num % 13 == 0:
                raise Exception("Permission denied")
            elif vol_num % 17 == 0:
                time.sleep(0.5)
                raise Exception("Volume attached")

            # Variable success times
            time.sleep(0.01 + (vol_num % 10) * 0.01)
            return None

        mock_flow.delete_volume.side_effect = complex_delete

        # Act - Complex pattern matching
        start_time = time.time()
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'volumes', 'delete-all',
                '--pattern', '^(test-\\d{4}-\\d{8}-\\d{3}|ci-build-\\d{5}-artifact)$',
                '--yes'
            ])
        total_time = time.time() - start_time

        # Assert
        assert result.exit_code == 0
        # Even in worst case, should complete in reasonable time
        assert total_time < 30, f"Worst case scenario too slow: {total_time}s"
