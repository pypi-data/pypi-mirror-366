"""Integration tests for SSH functionality.

These tests focus on integration points without mocking subprocess or
other external dependencies we don't own.
"""

import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from flow.api.models import Task, TaskConfig, TaskStatus
from flow.providers.fcp.provider import FCPProvider


class TestSSHLogRetrieval:
    """Integration tests for SSH-based log retrieval."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock FCP provider for log testing."""
        provider = Mock(spec=FCPProvider)
        provider.get_task_logs = Mock(return_value="Mock log output")
        provider.stream_task_logs = Mock(return_value=iter(["Log line 1", "Log line 2"]))
        return provider

    @pytest.fixture
    def task_with_provider(self, mock_provider):
        """Create a task with a mocked provider for log testing."""
        task = Task(
            task_id="test-task-123",
            name="test-task",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="test-task",
                instance_type="a100",
                command=["echo", "test"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            ssh_host="1.2.3.4",
            ssh_port=22,
            ssh_user="ubuntu"
        )
        task._provider = mock_provider
        return task

    def test_log_retrieval_integration(self, task_with_provider):
        """Test that logs method properly delegates to provider."""
        # Test get_task_logs
        logs = task_with_provider.logs(tail=100)
        assert logs == "Mock log output"
        task_with_provider._provider.get_task_logs.assert_called_with(
            "test-task-123",
            tail=100
        )

        # Test stream_task_logs
        log_lines = list(task_with_provider.logs(follow=True))
        assert log_lines == ["Log line 1", "Log line 2"]
        task_with_provider._provider.stream_task_logs.assert_called_with(
            "test-task-123"
        )

    def test_ssh_environment_variables(self):
        """Test SSH configuration from environment variables."""
        # Test that environment variables are properly formatted
        with patch.dict(os.environ, {
            'FCP_SSH_USER': 'testuser',
            'FCP_SSH_PORT': '2222'
        }):
            assert os.getenv('FCP_SSH_USER', 'ubuntu') == 'testuser'
            assert int(os.getenv('FCP_SSH_PORT', '22')) == 2222


class TestSSHKeyIntegration:
    """Integration tests for SSH key security validation."""

    def test_ssh_key_security_validation(self):
        """Test SSH key permission validation."""
        from pathlib import Path

        from flow.errors import ValidationError
        from flow.utils.security import check_ssh_key_permissions

        with patch('pathlib.Path.stat') as mock_stat:
            with patch('pathlib.Path.exists', return_value=True):
                # Test secure permissions (600)
                mock_stat.return_value = Mock(st_mode=0o100600)
                check_ssh_key_permissions(Path("/home/user/.ssh/id_rsa"))  # Should not raise

                # Test insecure permissions (644)
                mock_stat.return_value = Mock(st_mode=0o100644)
                with pytest.raises(ValidationError) as exc_info:
                    check_ssh_key_permissions(Path("/home/user/.ssh/id_rsa"))
                assert "insecure permissions" in str(exc_info.value)
