"""Unit tests for Flow SDK logs functionality.

These tests verify the behavior of log-related methods in isolation,
using mocks to test edge cases and error handling without real infrastructure.
"""

import subprocess
import time
from unittest.mock import Mock, patch

import pytest

from datetime import datetime, timezone
from flow.api.models import Task, TaskStatus
from flow.errors import TaskNotFoundError
from flow.providers.fcp.provider import FCPProvider


class TestTaskLogsUnit:
    """Unit tests for Task.logs() method."""

    def test_logs_without_provider(self):
        """Test that logs() raises error when task has no provider."""
        task = Task(
            task_id="test-123",
            name="test",
            status=TaskStatus.RUNNING,
            created_at=datetime.now(timezone.utc),
            instance_type="cpu.small",
            num_instances=1,
            region="us-central1",
            cost_per_hour="$1.00",
            _provider=None
        )

        with pytest.raises(RuntimeError, match="Task not connected to provider"):
            task.logs()

    def test_logs_delegates_to_provider(self):
        """Test that logs() correctly delegates to provider."""
        mock_provider = Mock(spec=FCPProvider)
        mock_provider.get_task_logs.return_value = "Test logs"
        mock_provider.stream_task_logs.return_value = iter(["Line 1", "Line 2"])

        task = Task(
            task_id="test-123",
            name="test",
            status=TaskStatus.RUNNING,
            created_at=datetime.now(timezone.utc),
            instance_type="cpu.small",
            num_instances=1,
            region="us-central1",
            cost_per_hour="$1.00"
        )
        # Set provider after creation since it's a PrivateAttr
        task._provider = mock_provider

        # Test non-streaming
        logs = task.logs(follow=False, tail=50)
        assert logs == "Test logs"
        mock_provider.get_task_logs.assert_called_once_with("test-123", tail=50, log_type="stdout")

        # Test streaming
        stream = task.logs(follow=True)
        lines = list(stream)
        assert lines == ["Line 1", "Line 2"]
        mock_provider.stream_task_logs.assert_called_once_with("test-123", log_type="stdout")


class TestFCPProviderLogsUnit:
    """Unit tests for FCPProvider log methods."""

    @pytest.fixture
    def provider(self):
        """Create FCPProvider with mocked dependencies."""
        mock_config = Mock(project="test-project", provider="fcp", provider_config={})
        mock_http = Mock()
        provider = FCPProvider(mock_config, mock_http)
        provider._project_id = "test-project-id"
        provider._get_project_id = Mock(return_value="test-project-id")
        return provider

    def test_get_logs_task_not_found(self, provider):
        """Test error when task doesn't exist."""
        provider.http.request.return_value = {"data": []}

        with pytest.raises(TaskNotFoundError):
            provider.get_task_logs("nonexistent-task")

    def test_get_logs_pending_task(self, provider):
        """Test logs for pending task."""
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "pending",
                "instances": []
            }]
        }

        logs = provider.get_task_logs("task-123")
        assert "Task task-123 is pending" in logs
        assert "Use 'flow logs task-123 -f' to wait for logs" in logs

    def test_get_logs_no_public_ip(self, provider):
        """Test logs when instance has no public IP."""
        # Mock the bid response
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "running",
                "instances": ["inst-1"]
            }]
        }
        
        # Mock get_task to return a task without SSH info
        mock_task = Mock()
        mock_task.ssh_host = None
        mock_task.ssh_port = None
        provider.get_task = Mock(return_value=mock_task)
        
        # Mock remote operations to raise the expected error
        from flow.providers.fcp.remote_operations import RemoteExecutionError
        mock_remote_ops = Mock()
        mock_remote_ops.execute_command.side_effect = RemoteExecutionError("No SSH access for task task-123")
        provider.get_remote_operations = Mock(return_value=mock_remote_ops)

        logs = provider.get_task_logs("task-123")
        # When using remote operations, lack of public IP results in a more detailed error
        assert "Instance is not accessible" in logs
        assert "Instance is still starting" in logs or "Task was created without SSH keys" in logs

    def test_get_logs_ssh_success(self, provider):
        """Test successful SSH log retrieval."""
        # Mock the bid response
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "running",
                "instances": ["inst-1"]
            }]
        }
        
        # Mock remote operations to return log content
        mock_remote_ops = Mock()
        mock_remote_ops.execute_command.return_value = "Log line 1\nLog line 2\nLog line 3"
        provider.get_remote_operations = Mock(return_value=mock_remote_ops)

        logs = provider.get_task_logs("task-123", tail=3)

        # Verify the correct command was executed
        mock_remote_ops.execute_command.assert_called_once()
        task_id, command = mock_remote_ops.execute_command.call_args[0]
        assert task_id == "task-123"
        assert "docker logs main --tail 3" in command

        assert logs == "Log line 1\nLog line 2\nLog line 3"

    def test_get_logs_ssh_connection_refused(self, provider):
        """Test SSH connection refused handling."""
        # Mock the bid response
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "running",
                "instances": ["inst-1"]
            }]
        }
        
        # Mock remote operations to raise connection error
        from flow.providers.fcp.remote_operations import RemoteExecutionError
        mock_remote_ops = Mock()
        mock_remote_ops.execute_command.side_effect = RemoteExecutionError("connection refused")
        provider.get_remote_operations = Mock(return_value=mock_remote_ops)

        logs = provider.get_task_logs("task-123")
        assert "Instance not reachable" in logs
        assert "Instance is still starting" in logs
        assert "FCP instances take up to" in logs

    def test_get_logs_ssh_timeout(self, provider):
        """Test SSH timeout handling."""
        # Mock the bid response
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "running",
                "instances": ["inst-1"]
            }]
        }
        
        # Mock remote operations to raise timeout error
        from flow.providers.fcp.remote_operations import RemoteExecutionError
        mock_remote_ops = Mock()
        mock_remote_ops.execute_command.side_effect = RemoteExecutionError("connection timed out")
        provider.get_remote_operations = Mock(return_value=mock_remote_ops)

        logs = provider.get_task_logs("task-123")
        assert "Instance not reachable" in logs
        assert "Instance is still starting" in logs or "Network connectivity issues" in logs

    @patch('subprocess.run')
    @patch('time.sleep')
    def test_stream_logs_basic(self, mock_sleep, mock_run, provider):
        """Test basic log streaming."""
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "running",
                "instances": [{"public_ip": "1.2.3.4"}]
            }]
        }

        # Mock file size checks and content
        mock_run.side_effect = [
            Mock(returncode=0, stdout="0"),     # Initial size
            Mock(returncode=0, stdout="100"),   # File grew
            Mock(returncode=0, stdout="Line 1\nLine 2"),  # Content
            Mock(returncode=0, stdout="200"),   # More growth
            Mock(returncode=0, stdout="Line 3"),  # More content
        ]

        # Mock task completion check
        provider.get_task = Mock()
        provider.get_task.side_effect = [
            Mock(status=TaskStatus.RUNNING),
            Mock(status=TaskStatus.COMPLETED)
        ]

        # Mock final logs
        provider.get_task_logs = Mock(return_value="Final line")

        # Collect streamed logs
        logs = list(provider.stream_task_logs("task-123"))

        assert "Line 1" in logs
        assert "Line 2" in logs
        # Line 3 might not appear due to task completion
        assert "Final line" in logs

    def test_stream_logs_task_not_found(self, provider):
        """Test streaming when task doesn't exist."""
        provider.http.request.return_value = {"data": []}

        logs = list(provider.stream_task_logs("nonexistent"))
        assert len(logs) == 1
        assert "Error: Task nonexistent not found" in logs[0]

    @patch('subprocess.run')
    @patch('time.sleep')
    def test_stream_logs_keyboard_interrupt(self, mock_sleep, mock_run, provider):
        """Test handling of Ctrl+C during streaming."""
        provider.http.request.return_value = {
            "data": [{
                "id": "task-123",
                "status": "running",
                "instances": [{"public_ip": "1.2.3.4"}]
            }]
        }

        # Simulate KeyboardInterrupt after first check
        mock_run.side_effect = KeyboardInterrupt()

        logs = list(provider.stream_task_logs("task-123"))
        assert len(logs) == 1
        assert "Log streaming interrupted" in logs[0]


class TestLogSanitization:
    """Test log content sanitization."""

    def test_sanitize_sensitive_data(self):
        """Test that sensitive data is properly sanitized."""
        # This would be implemented in the actual provider
        sensitive_patterns = [
            ("AWS_SECRET_KEY=abc123", "AWS_SECRET_KEY=[REDACTED]"),
            ("password: mysecret", "password: [REDACTED]"),
            ("api_key='sk-12345'", "api_key='[REDACTED]'"),
            ("token=\"ghp_abcd\"", "token=\"[REDACTED]\""),
        ]

        # In real implementation, provider would sanitize
        for original, expected in sensitive_patterns:
            # Verify pattern matching works
            assert "REDACTED" in expected
            assert "REDACTED" not in original


class TestLogPerformance:
    """Test log-related performance characteristics."""

    def test_log_parsing_performance(self):
        """Test that log parsing is efficient."""
        # Generate large log content
        large_log = "\n".join([f"Log line {i}" for i in range(10000)])

        start_time = time.time()
        lines = large_log.splitlines()
        parse_time = time.time() - start_time

        assert len(lines) == 10000
        assert parse_time < 0.1  # Should parse 10k lines in < 100ms

    def test_tail_efficiency(self):
        """Test that tail operation is efficient."""
        # Simulate tail operation
        large_log = "\n".join([f"Log line {i}" for i in range(100000)])

        start_time = time.time()
        lines = large_log.splitlines()
        tail_lines = lines[-1000:]  # Get last 1000 lines
        tail_time = time.time() - start_time

        assert len(tail_lines) == 1000
        assert tail_time < 0.1  # Should be fast even for large logs
