"""Integration tests for the mount CLI command."""

import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner

from flow import Flow
from flow.api.models import Task, Volume, TaskStatus, StorageInterface
from datetime import datetime, timezone
from flow.errors import ValidationError
from flow.providers.fcp.remote_operations import RemoteExecutionError
from flow.cli.app import cli


class TestMountCommand:
    """Test suite for 'flow mount' CLI command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def mock_flow_client(self):
        """Create a mock Flow client."""
        mock = Mock(spec=Flow)
        return mock

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return Task(
            task_id="task_abc123",
            name="gpu-training",
            status=TaskStatus.RUNNING,
            created_at=datetime.now(timezone.utc),
            instance_type="a100-80gb",
            num_instances=1,
            cost_per_hour="$10.00",
            region="us-central1-b",
            instances=["inst_123"],
            ssh_host="1.2.3.4",
            ssh_port=22,
        )

    @pytest.fixture
    def sample_volume(self):
        """Create a sample volume."""
        return Volume(
            volume_id="vol_xyz789",
            name="training-data",
            size_gb=100,
            region="us-central1-b",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now(timezone.utc),
            attached_to=[],
        )

    @patch("flow.Flow")
    def test_mount_success(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test successful volume mount via CLI."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.return_value = None

        # Run command
        result = runner.invoke(cli, ["mount", "vol_xyz789", "task_abc123"])

        # Check output
        assert result.exit_code == 0
        assert "Mounting volume" in result.output
        assert "training-data" in result.output
        assert "gpu-training" in result.output
        assert "Volume mounted successfully" in result.output
        assert "/mnt/training-data" in result.output

        # Verify method calls
        mock_flow_client.mount_volume.assert_called_once_with("vol_xyz789", "task_abc123")

    @patch("flow.Flow")
    def test_mount_by_name(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test mounting by volume name."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.return_value = None

        # Run command with names instead of IDs
        result = runner.invoke(cli, ["mount", "training-data", "gpu-training"])

        # Check success
        assert result.exit_code == 0
        assert "Volume mounted successfully" in result.output

        # Verify resolved to correct IDs
        mock_flow_client.mount_volume.assert_called_once_with("vol_xyz789", "task_abc123")

    @patch("flow.Flow")
    def test_mount_by_index(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test mounting using index notation."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.list_tasks.return_value = [sample_task]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.return_value = None

        # Mock cache files
        with patch(
            "flow.cli.utils.volume_index_cache.VolumeIndexCache.load_indices"
        ) as mock_vol_cache:
            with patch(
                "flow.cli.utils.task_index_cache.TaskIndexCache.load_indices"
            ) as mock_task_cache:
                mock_vol_cache.return_value = {"1": "vol_xyz789"}
                mock_task_cache.return_value = {"1": "task_abc123"}

                # Run command with indices
                result = runner.invoke(cli, ["mount", ":1", ":1"])

        # Check success
        assert result.exit_code == 0
        assert "Volume mounted successfully" in result.output

    @patch("flow.Flow")
    def test_mount_volume_not_found(self, mock_flow_class, runner, mock_flow_client):
        """Test error when volume not found."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = []  # No volumes

        # Run command
        result = runner.invoke(cli, ["mount", "nonexistent", "task_abc123"])

        # Check error
        assert result.exit_code == 0  # Click doesn't set exit code for our errors
        assert "Error:" in result.output
        assert "not found" in result.output

    @patch("flow.Flow")
    def test_mount_task_not_found(self, mock_flow_class, runner, mock_flow_client, sample_volume):
        """Test error when task not found."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.list_tasks.return_value = []  # No tasks

        # Run command
        result = runner.invoke(cli, ["mount", "vol_xyz789", "nonexistent"])

        # Check error
        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "not found" in result.output

    @patch("flow.Flow")
    def test_mount_validation_error(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test handling of validation errors."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.side_effect = ValidationError(
            "Region mismatch: task is in us-central1-b, volume is in eu-central1-a"
        )

        # Run command
        result = runner.invoke(cli, ["mount", "vol_xyz789", "task_abc123"])

        # Check error output
        assert "Validation Error:" in result.output
        assert "Region mismatch" in result.output

    @patch("flow.Flow")
    def test_mount_ssh_failure(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test handling of SSH mount failures."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.side_effect = RemoteExecutionError("SSH connection failed")

        # Run command
        result = runner.invoke(cli, ["mount", "vol_xyz789", "task_abc123"])

        # Check error and troubleshooting output
        assert "Mount Failed:" in result.output
        assert "SSH connection failed" in result.output
        assert "Troubleshooting:" in result.output
        assert "Ensure the task is fully running" in result.output

    @patch("flow.Flow")
    def test_mount_task_not_running_warning(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test warning when task is not in running state."""
        # Setup task in pending state
        sample_task.status = TaskStatus.PENDING

        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.return_value = None

        # Run command
        result = runner.invoke(cli, ["mount", "vol_xyz789", "task_abc123"])

        # Check warning
        assert "Warning:" in result.output
        assert "Task is pending" in result.output
        assert "Mount may fail" in result.output

    @patch("flow.Flow")
    def test_mount_shows_next_actions(
        self, mock_flow_class, runner, mock_flow_client, sample_task, sample_volume
    ):
        """Test that successful mount shows helpful next actions."""
        # Setup mock
        mock_flow_class.return_value = mock_flow_client
        mock_flow_client.list_volumes.return_value = [sample_volume]
        mock_flow_client.get_task.return_value = sample_task
        mock_flow_client.mount_volume.return_value = None

        # Run command
        result = runner.invoke(cli, ["mount", "vol_xyz789", "task_abc123"])

        # Check next actions
        assert "flow ssh task_abc123" in result.output
        assert "df -h /mnt/training-data" in result.output
        assert "flow volumes list" in result.output
