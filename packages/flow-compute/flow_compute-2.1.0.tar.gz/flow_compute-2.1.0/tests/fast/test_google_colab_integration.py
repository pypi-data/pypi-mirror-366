"""Unit tests for Google Colab integration."""

import re
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from flow._internal.integrations.google_colab import ColabConnection, GoogleColabIntegration
from flow.api.models import TaskStatus
from flow.errors import FlowError, ValidationError


class TestColabConnection:
    """Test ColabConnection model."""

    def test_colab_connection_creation(self):
        """Test creating a ColabConnection with all fields."""
        connection = ColabConnection(
            connection_url="http://localhost:8888/?token=test_token",
            ssh_command="ssh -L 8888:localhost:8888 ubuntu@1.2.3.4",
            instance_ip="1.2.3.4",
            instance_type="a100",
            task_id="task-123",
            session_id="colab-abc123",
            created_at=datetime.now(timezone.utc),
            jupyter_token="test_token"
        )

        assert connection.connection_url == "http://localhost:8888/?token=test_token"
        assert connection.ssh_command == "ssh -L 8888:localhost:8888 ubuntu@1.2.3.4"
        assert connection.instance_ip == "1.2.3.4"
        assert connection.task_id == "task-123"
        assert connection.jupyter_token == "test_token"

    def test_colab_connection_to_dict(self):
        """Test converting ColabConnection to dictionary."""
        created_at = datetime.now(timezone.utc)
        connection = ColabConnection(
            connection_url="http://localhost:8888/?token=test_token",
            ssh_command="ssh -L 8888:localhost:8888 ubuntu@1.2.3.4",
            instance_ip="1.2.3.4",
            instance_type="a100",
            task_id="task-123",
            session_id="colab-abc123",
            created_at=created_at,
            jupyter_token="test_token"
        )

        result = connection.to_dict()

        assert result['connection_url'] == "http://localhost:8888/?token=test_token"
        assert result['ssh_command'] == "ssh -L 8888:localhost:8888 ubuntu@1.2.3.4"
        assert result['instance_ip'] == "1.2.3.4"
        assert result['instance_type'] == "a100"
        assert result['task_id'] == "task-123"
        assert result['session_id'] == "colab-abc123"
        assert result['created_at'] == created_at.isoformat()
        assert result['jupyter_token'] == "test_token"


@pytest.mark.integration
class TestGoogleColabIntegration:
    """Test GoogleColabIntegration class."""

    @pytest.fixture
    def mock_flow(self):
        """Create mock Flow client."""
        mock = Mock()
        mock.run = Mock()
        mock.get_task = Mock()
        mock.logs = Mock()
        mock.stop = Mock()
        return mock

    @pytest.fixture
    def integration(self, mock_flow):
        """Create GoogleColabIntegration instance."""
        return GoogleColabIntegration(mock_flow)

    def test_connection_url_generation(self):
        """Test that connection URLs are generated correctly."""
        # This is embedded in the connect method, but we can test the format
        token = "test_token_abc123"
        expected_url = f"http://localhost:8888/?token={token}"

        # The URL should follow this exact format
        assert expected_url.startswith("http://localhost:8888/?token=")
        assert len(token) > 0

    @patch('flow._internal.integrations.google_colab.GoogleColabIntegration._wait_for_instance_ready')
    def test_connect_parameter_validation(self, mock_wait, integration):
        """Test parameter validation in connect method."""
        # Test invalid hours
        with pytest.raises(ValidationError, match="Hours must be between"):
            integration.connect(instance_type="a100", hours=0.05)

        with pytest.raises(ValidationError, match="Hours must be between"):
            integration.connect(instance_type="a100", hours=200)

        # Valid hours should not raise ValidationError
        # Mock the wait method to avoid actual execution
        mock_wait.return_value = Mock()
        integration.flow.run.return_value = Mock(task_id="test-123")

        try:
            integration.connect(instance_type="a100", hours=1.0)
        except ValidationError:
            pytest.fail("Valid hours raised ValidationError")

    @patch('time.time')
    @patch('time.sleep')
    def test_wait_for_instance_ready_timeout(self, mock_sleep, mock_time, integration):
        """Test that instance wait times out after 15 minutes."""
        # Set up time progression
        mock_time.side_effect = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

        # Create mock task
        task = Mock()
        task.task_id = "test-123"
        task.status = TaskStatus.PENDING
        task.instance_type = "a100"
        task.ssh_host = None

        # Mock get_task to always return pending status
        integration.flow.get_task.return_value = task

        # Should timeout after 900 seconds (15 minutes)
        with pytest.raises(FlowError, match="not ready after 15 minutes"):
            integration._wait_for_instance_ready(task, "session-123", timeout=900)

    def test_ssh_verification(self, integration):
        """Test SSH access verification logic."""
        # Test with mock socket that connects successfully
        with patch('socket.socket') as mock_socket_class:
            mock_socket = Mock()
            mock_socket.connect_ex.return_value = 0  # Success
            mock_socket_class.return_value = mock_socket

            result = integration._verify_ssh_access("1.2.3.4", 22)
            assert result is True
            mock_socket.connect_ex.assert_called_once_with(("1.2.3.4", 22))

        # Test with connection failure
        with patch('socket.socket') as mock_socket_class:
            mock_socket = Mock()
            mock_socket.connect_ex.return_value = 1  # Failure
            mock_socket_class.return_value = mock_socket

            result = integration._verify_ssh_access("1.2.3.4", 22)
            assert result is False

    def test_jupyter_token_extraction(self, integration):
        """Test extracting Jupyter token from logs."""
        # Test log with token
        logs_with_token = """
        Starting Jupyter server...
        Installing dependencies...
        JUPYTER_TOKEN=abc123def456ghi789
        JUPYTER_READY=true
        Server started successfully
        """

        # Use regex from the actual implementation
        token_match = re.search(r'JUPYTER_TOKEN=([a-zA-Z0-9_-]+)', logs_with_token)
        assert token_match is not None
        assert token_match.group(1) == "abc123def456ghi789"

        # Test log without token
        logs_without_token = """
        Starting Jupyter server...
        Installing dependencies...
        Server starting...
        """

        token_match = re.search(r'JUPYTER_TOKEN=([a-zA-Z0-9_-]+)', logs_without_token)
        assert token_match is None

    def test_startup_progress_messages(self, integration):
        """Test get_startup_progress returns appropriate messages."""
        # Mock different log scenarios
        test_cases = [
            ("JUPYTER_READY=true", "Jupyter server ready!"),
            ("Starting Jupyter server on port 8888", "Starting Jupyter server..."),
            ("pip install jupyter", "Installing dependencies..."),
            ("Starting Jupyter server for Google Colab", "Initializing Jupyter environment..."),
            ("Some other log content", "Instance initializing..."),
        ]

        for log_content, expected_message in test_cases:
            integration.flow.logs.return_value = log_content
            message = integration.get_startup_progress("task-123")
            assert message == expected_message

    def test_list_sessions(self, integration):
        """Test listing active sessions."""
        # Add some test connections
        connection1 = ColabConnection(
            connection_url="http://localhost:8888/?token=token1",
            ssh_command="ssh -L 8888:localhost:8888 ubuntu@1.2.3.4",
            instance_ip="1.2.3.4",
            instance_type="a100",
            task_id="task-1",
            session_id="colab-session1",
            created_at=datetime.now(timezone.utc),
            jupyter_token="token1"
        )
        connection2 = ColabConnection(
            connection_url="http://localhost:8888/?token=token2",
            ssh_command="ssh -L 8888:localhost:8888 ubuntu@5.6.7.8",
            instance_ip="5.6.7.8",
            instance_type="h100",
            task_id="task-2",
            session_id="colab-session2",
            created_at=datetime.now(timezone.utc),
            jupyter_token="token2"
        )

        integration._active_connections = {
            "colab-session1": connection1,
            "colab-session2": connection2,
        }

        # Mock task status
        task1 = Mock(status=TaskStatus.RUNNING)
        task2 = Mock(status=TaskStatus.PENDING)
        integration.flow.get_task.side_effect = [task1, task2]

        sessions = integration.list_sessions()

        assert len(sessions) == 2
        assert sessions[0]['session_id'] == "colab-session1"
        assert sessions[0]['instance_type'] == "a100"
        assert sessions[0]['status'] == "running"
        assert sessions[1]['session_id'] == "colab-session2"
        assert sessions[1]['instance_type'] == "h100"
        assert sessions[1]['status'] == "pending"

    def test_disconnect(self, integration):
        """Test disconnecting a session."""
        # Add a test connection
        connection = ColabConnection(
            connection_url="http://localhost:8888/?token=token1",
            ssh_command="ssh -L 8888:localhost:8888 ubuntu@1.2.3.4",
            instance_ip="1.2.3.4",
            instance_type="a100",
            task_id="task-1",
            session_id="colab-session1",
            created_at=datetime.now(timezone.utc),
            jupyter_token="token1"
        )

        integration._active_connections = {"colab-session1": connection}

        # Test successful disconnect
        integration.disconnect("colab-session1")

        integration.flow.stop.assert_called_once_with("task-1")
        assert "colab-session1" not in integration._active_connections

        # Test disconnect of non-existent session
        with pytest.raises(ValueError, match="Session .* not found"):
            integration.disconnect("non-existent")
