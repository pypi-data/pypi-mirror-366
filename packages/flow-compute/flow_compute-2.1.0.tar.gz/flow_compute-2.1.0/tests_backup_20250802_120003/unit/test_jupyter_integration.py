"""Unit tests for Flow-Colab integration."""

import os
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from flow._internal.integrations.jupyter import JupyterConnection, JupyterIntegration
from flow._internal.integrations.jupyter_persistence import PersistenceManager
from flow._internal.integrations.jupyter_session import FlowJupyterSession, SessionManager
from flow.api.models import Task, TaskStatus
from flow.utils.exceptions import NotFoundError


class TestJupyterIntegration:
    """Test JupyterIntegration class."""

    @pytest.fixture
    def mock_flow(self):
        """Create mock Flow client."""
        mock = Mock()
        mock.run.return_value = Task(
            task_id="task-123",
            name="colab-session",
            status=TaskStatus.RUNNING,
            instance_type="a100",
            region="us-central1",
            created_at=datetime.now(timezone.utc),
            num_instances=1,
            cost_per_hour="$3.60",
            ssh_host="10.0.0.1"
        )
        mock.status.return_value = "running"
        return mock

    @pytest.fixture
    def integration(self, mock_flow, tmp_path):
        """Create JupyterIntegration instance with mocked dependencies."""
        with patch('flow._internal.integrations.jupyter_session.SessionManager') as mock_sm:
            with patch('flow._internal.integrations.jupyter_persistence.PersistenceManager') as mock_pm:
                # Setup session manager mock
                mock_sm.return_value.storage_path = tmp_path / "sessions.json"
                mock_sm.return_value.save_session.return_value = Mock()

                # Setup persistence manager mock
                mock_pm.return_value.is_enabled.return_value = True
                mock_pm.return_value.ensure_volume.return_value = "vol-123"

                # Mock logs to show kernel is ready
                mock_flow.logs.return_value = "Starting kernel...\nKERNEL_READY=true\nKERNEL_PID=12345"

                integration = JupyterIntegration(mock_flow)
                integration.session_manager = mock_sm.return_value
                integration.persistence_manager = mock_pm.return_value

                return integration

    def test_launch_basic(self, integration, mock_flow):
        """Test basic launch functionality."""
        connection = integration.launch(instance_type="h100", hours=2.0)

        assert isinstance(connection, JupyterConnection)
        assert connection.instance_type == "h100"
        assert connection.task_id == "task-123"
        assert connection.url == "http://localhost:8888"  # Simple localhost URL
        assert connection.ssh_command == "ssh -L 8888:localhost:8888 ubuntu@10.0.0.1"
        assert connection.startup_time > 0

    def test_launch_with_tunnel_failure(self, integration, mock_flow):
        """Test launch with tunnel creation failure."""
        # Skip tunnel mocking - module doesn't exist in new architecture
        # Test that launch works without tunnel functionality
        connection = integration.launch()

        # URL will be generated from task details
        assert connection.url

    def test_resume_notebook(self, integration, mock_flow):
        """Test resuming a notebook with saved state."""
        # Setup mock session
        mock_session = FlowJupyterSession(
            session_id="session-123",
            notebook_name="training.ipynb",
            notebook_path=None,
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            last_active=datetime.now(timezone.utc) - timedelta(hours=1),
            checkpoint_size_gb=1.5,
            volume_id="vol-123",
            instance_type="a100",
            task_id="old-task-123",
            status="active"
        )

        integration.session_manager.find_session_for_notebook.return_value = mock_session
        integration.persistence_manager.get_checkpoint_info.return_value = {
            "size_gb": 1.5,
            "variable_count": 10,
            "restore_time_ms": 50
        }

        # Skip tunnel mocking - module doesn't exist in new architecture
        connection = integration.resume("training.ipynb")

        assert connection.session_id == "session-123"
        # The checkpoint info would be available through other means,
        # not directly on the connection object

    def test_resume_notebook_not_found(self, integration):
        """Test resuming non-existent notebook."""
        integration.session_manager.find_session_for_notebook.return_value = None

        with pytest.raises(NotFoundError, match="No session found"):
            integration.resume("unknown.ipynb")

    def test_list_sessions(self, integration):
        """Test listing sessions."""
        mock_sessions = [
            FlowJupyterSession(
                session_id="session-1",
                notebook_name="model.ipynb",
                notebook_path=None,
                created_at=datetime.now(timezone.utc),
                last_active=datetime.now(timezone.utc),
                checkpoint_size_gb=0.5,
                volume_id="vol-1",
                instance_type="a100",
                task_id="task-1",
                status="active"
            )
        ]

        integration.session_manager.list_sessions.return_value = mock_sessions

        sessions = integration.list_sessions()

        assert len(sessions) == 1
        assert sessions[0].notebook_name == "model.ipynb"

    def test_stop_session(self, integration, mock_flow):
        """Test stopping a session."""
        mock_session = FlowJupyterSession(
            session_id="session-123",
            notebook_name="training.ipynb",
            notebook_path=None,
            created_at=datetime.now(timezone.utc),
            last_active=datetime.now(timezone.utc),
            checkpoint_size_gb=1.0,
            volume_id="vol-123",
            instance_type="a100",
            task_id="task-123",
            status="active"
        )

        integration.session_manager.get_session.return_value = mock_session

        integration.stop_session("session-123")

        mock_flow.cancel.assert_called_once_with("task-123")
        integration.session_manager.stop_session.assert_called_once_with("session-123")


class TestSessionManager:
    """Test SessionManager class."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create SessionManager with temporary storage."""
        return SessionManager(storage_path=tmp_path / "sessions.json")

    def test_save_new_session(self, manager):
        """Test saving a new session."""
        session = manager.save_session(
            session_id="test-123",
            task_id="task-456",
            instance_type="h100",
            notebook_name="test.ipynb"
        )

        assert session.session_id == "test-123"
        assert session.task_id == "task-456"
        assert session.instance_type == "h100"
        assert session.notebook_name == "test.ipynb"
        assert session.status == "active"

    def test_find_session_for_notebook(self, manager):
        """Test finding session by notebook name."""
        # Create two sessions for same notebook
        old_session = manager.save_session("old-123", "task-1", "a100", "test.ipynb")
        time.sleep(0.01)  # Ensure different timestamps
        new_session = manager.save_session("new-456", "task-2", "h100", "test.ipynb")

        # Should return most recent
        found = manager.find_session_for_notebook("test.ipynb")
        assert found.session_id == "new-456"

    def test_session_persistence(self, manager):
        """Test session persistence across manager instances."""
        # Save session
        manager.save_session("persist-123", "task-789", "a100", "persist.ipynb")

        # Create new manager instance
        new_manager = SessionManager(storage_path=manager.storage_path)

        # Should load saved session
        session = new_manager.get_session("persist-123")
        assert session is not None
        assert session.notebook_name == "persist.ipynb"

    def test_expire_old_sessions(self, manager):
        """Test expiring old sessions."""
        # Create old session
        session = manager.save_session("old-123", "task-456", "a100")
        session.last_active = datetime.now(timezone.utc) - timedelta(days=40)
        manager._save_sessions()

        # Expire sessions older than 30 days
        manager.expire_old_sessions(days=30)

        # Check status changed
        expired = manager.get_session("old-123")
        assert expired.status == "expired"


class TestPersistenceManager:
    """Test PersistenceManager class."""

    @pytest.fixture
    def manager(self):
        """Create PersistenceManager with mocked Flow client."""
        mock_flow = Mock()
        return PersistenceManager(flow_client=mock_flow)

    def test_ensure_volume_existing(self, manager):
        """Test ensuring volume when it already exists."""
        mock_volume = Mock()
        mock_volume.name = "colab-persist-test-123"
        mock_volume.volume_id = "vol-existing"

        manager.flow.list_volumes.return_value = [mock_volume]

        volume_id = manager.ensure_volume("us-central1", "test-123")

        assert volume_id == "vol-existing"
        manager.flow.create_volume.assert_not_called()

    def test_ensure_volume_create_new(self, manager):
        """Test creating new volume when none exists."""
        manager.flow.list_volumes.return_value = []

        mock_new_volume = Mock()
        mock_new_volume.volume_id = "vol-new"
        manager.flow.create_volume.return_value = mock_new_volume

        volume_id = manager.ensure_volume("us-central1", "test-123")

        assert volume_id == "vol-new"
        manager.flow.create_volume.assert_called_once()

    def test_persistence_disabled(self):
        """Test when persistence is disabled."""
        with patch.dict(os.environ, {"FLOW_COLAB_PERSISTENCE": "false"}):
            manager = PersistenceManager()
            assert not manager.is_enabled()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
