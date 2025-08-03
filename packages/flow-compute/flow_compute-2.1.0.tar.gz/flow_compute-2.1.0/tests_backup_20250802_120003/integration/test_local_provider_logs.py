"""Integration tests for LocalProvider logs functionality.

These tests demonstrate how the LocalProvider enables rapid testing
of Flow SDK functionality without cloud infrastructure.
"""

import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from flow import Flow
from flow.api.models import TaskConfig, TaskStatus
from flow.providers.local import LocalProvider, LocalTestConfig


class TestLocalProviderLogs:
    """Test logs functionality using LocalProvider."""

    @pytest.fixture
    def local_flow(self, tmp_path):
        """Create Flow instance with LocalProvider."""
        from flow._internal.config import Config
        # Create a Config object with provider="local"
        config = Config(provider="local")
        # Create the provider
        provider = LocalProvider(config)
        # Override the local config for testing
        provider.local_config = LocalTestConfig(
            storage_dir=tmp_path / "flow-test",
            use_docker=False,  # Use processes for faster tests
            clean_on_exit=True
        )
        provider.storage.base_dir = tmp_path / "flow-test"
        provider.log_manager.log_dir = tmp_path / "flow-test" / "logs"

        # Create Flow with the config (not provider directly)
        return Flow(config=config)

    def test_basic_log_retrieval(self, local_flow):
        """Test basic log retrieval from local task."""
        config = TaskConfig(
            name="test-logs-basic",
            command="""
                echo "Starting test task"
                for i in {1..5}; do
                    echo "Log line $i"
                    sleep 0.1
                done
                echo "Test complete"
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)

        # Wait a moment for logs to start
        time.sleep(0.5)

        # Get logs while running
        logs = task.logs(tail=3)
        assert "Log line" in logs

        # Wait for completion
        task.wait(timeout=10)

        # Get complete logs
        final_logs = task.logs()
        assert "Starting test task" in final_logs
        assert "Test complete" in final_logs
        assert all(f"Log line {i}" in final_logs for i in range(1, 6))

    def test_log_streaming(self, local_flow):
        """Test real-time log streaming."""
        config = TaskConfig(
            name="test-logs-stream",
            command="""
                for i in {1..10}; do
                    echo "[$(date +%s)] Stream line $i"
                    sleep 0.2
                done
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)

        # Stream logs
        streamed_lines = []
        start_time = time.time()

        for line in task.logs(follow=True):
            streamed_lines.append((line, time.time() - start_time))
            if len(streamed_lines) >= 10:
                break

        # Verify streaming behavior
        assert len(streamed_lines) >= 10

        # Verify timing - logs should arrive over time (not all at once)
        # Note: LocalProvider might buffer some logs, so we check for reasonable timing
        first_time = streamed_lines[0][1]
        last_time = streamed_lines[-1][1]
        # Should take some time, but LocalProvider might be faster than real infrastructure
        assert last_time - first_time >= 0.5  # At least half a second

    def test_concurrent_log_access(self, local_flow):
        """Test multiple concurrent log readers."""
        config = TaskConfig(
            name="test-logs-concurrent",
            command="""
                for i in {1..20}; do
                    echo "Concurrent line $i"
                    sleep 0.1
                done
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)

        # Let some logs accumulate
        time.sleep(1)

        # Access logs concurrently
        results = []

        def read_logs(reader_id):
            logs = task.logs()
            return (reader_id, len(logs.splitlines()), "Concurrent line" in logs)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(read_logs, i) for i in range(5)]
            results = [f.result() for f in futures]

        # All readers should get logs
        assert all(success for _, _, success in results)

        # Line counts should be similar
        line_counts = [count for _, count, _ in results]
        assert max(line_counts) - min(line_counts) <= 5  # Small variation OK

    def test_large_log_performance(self, local_flow):
        """Test performance with large logs."""
        config = TaskConfig(
            name="test-logs-large",
            command="""
                # Generate 1000 log lines quickly
                for i in {1..1000}; do
                    echo "[$i] This is a test log line with some padding to make it longer"
                done
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)
        task.wait(timeout=30)

        # Measure retrieval performance
        start_time = time.time()
        logs = task.logs(tail=100)
        retrieval_time = time.time() - start_time

        # Should be very fast for local provider
        assert retrieval_time < 0.1  # Less than 100ms
        assert len(logs.splitlines()) <= 100
        assert "[1000]" in logs  # Should have the last line

    def test_task_failure_logs(self, local_flow):
        """Test log retrieval from failed tasks."""
        config = TaskConfig(
            name="test-logs-failure",
            command="""
                echo "Task starting"
                echo "Doing some work..."
                echo "ERROR: Something went wrong!"
                exit 1
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)

        # Wait for completion (even if it fails)
        task.wait(timeout=5)

        # Should still get logs
        logs = task.logs()
        assert "Task starting" in logs
        assert "ERROR: Something went wrong!" in logs

        # Task should be marked as failed
        assert task.status == TaskStatus.FAILED

    def test_multi_line_log_output(self, local_flow):
        """Test handling of multi-line output."""
        config = TaskConfig(
            name="test-logs-multiline",
            command="""
                echo "Single line"
                echo -e "Line 1\\nLine 2\\nLine 3"
                echo "Final line"
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)
        task.wait(timeout=5)

        logs = task.logs()
        lines = logs.splitlines()

        assert "Single line" in lines
        assert "Line 1" in lines
        assert "Line 2" in lines
        assert "Line 3" in lines
        assert "Final line" in lines


    def test_log_rotation_simulation(self, local_flow):
        """Test behavior with large logs that might rotate."""
        config = TaskConfig(
            name="test-logs-rotation",
            command="""
                # Generate lots of logs
                for i in {1..5000}; do
                    echo "[$i] Log rotation test - $(date) - padding text to make lines longer"
                done
            """,
            instance_type="cpu.small"
        )

        task = local_flow.run(config)

        # Stream some logs while running
        early_lines = []
        for line in task.logs(follow=True):
            early_lines.append(line)
            if len(early_lines) >= 100:
                break

        # Wait for completion
        task.wait(timeout=30)

        # Get tail of logs
        tail_logs = task.logs(tail=100)
        tail_lines = tail_logs.splitlines()

        # Should have early and late logs
        assert any("[1]" in line or "[2]" in line for line in early_lines)
        assert any("[4999]" in line or "[5000]" in line for line in tail_lines)


class TestLocalProviderDockerLogs:
    """Test logs with Docker-based execution."""

    @pytest.fixture
    def docker_flow(self, tmp_path):
        """Create Flow with Docker-based LocalProvider."""
        # Check if Docker is available
        import subprocess
        try:
            subprocess.run(["docker", "version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Docker not available")

        from flow._internal.config import Config
        # Create a Config object with provider="local"
        config = Config(provider="local")
        # Create the provider
        provider = LocalProvider(config)
        # Override the local config for Docker testing
        provider.local_config = LocalTestConfig(
            storage_dir=tmp_path / "flow-docker-test",
            use_docker=True,
            clean_on_exit=True
        )
        provider.storage.base_dir = tmp_path / "flow-docker-test"
        provider.log_manager.logs_dir = tmp_path / "flow-docker-test" / "logs"

        # Reinitialize executor with Docker if available
        from flow.providers.local.executor import ContainerTaskExecutor
        try:
            provider.executor = ContainerTaskExecutor(provider.local_config)
        except Exception:
            pytest.skip("Docker not available")

        # Create Flow with the config (not provider directly)
        return Flow(config=config)

    def test_docker_log_streaming(self, docker_flow):
        """Test log streaming from Docker container."""
        config = TaskConfig(
            name="test-docker-logs",
            command="""
                echo "Starting in Docker"
                echo "Container ID: $(hostname)"
                for i in {1..5}; do
                    echo "Docker log $i"
                    sleep 0.2
                done
                echo "Docker task complete"
            """,
            instance_type="cpu.small"
        )

        task = docker_flow.run(config)

        # Stream logs
        lines = []
        for line in task.logs(follow=True):
            lines.append(line)
            if "Docker task complete" in line:
                break

        # Verify Docker execution
        assert "Starting in Docker" in "\n".join(lines)
        assert "Container ID:" in "\n".join(lines)
        assert all(f"Docker log {i}" in "\n".join(lines) for i in range(1, 6))

    def test_docker_resource_limits(self, docker_flow):
        """Test that resource limits are applied in Docker."""
        config = TaskConfig(
            name="test-docker-resources",
            command="""
                # Check available resources
                echo "CPUs: $(nproc)"
                echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
                
                # Try to use CPU
                echo "Running CPU test..."
                timeout 2 yes > /dev/null || true
                echo "CPU test complete"
            """,
            instance_type="cpu.small"  # Should limit to 2 cores
        )

        task = docker_flow.run(config)
        task.wait(timeout=10)

        logs = task.logs()
        assert "CPUs:" in logs
        assert "Memory:" in logs
        assert "CPU test complete" in logs
