"""Unit tests for volume mounting functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from flow.api.models import Task, Volume, TaskStatus, StorageInterface
from datetime import datetime, timezone
from flow.errors import (
    ResourceNotFoundError,
    TaskNotFoundError,
    ValidationError,
)
from flow.providers.fcp.core.errors import FCPAPIError
from flow.providers.fcp.remote_operations import RemoteExecutionError
from flow.providers.fcp.provider import FCPProvider
from flow.providers.fcp.remote_operations import FCPRemoteOperations


class TestMountVolume:
    """Test suite for FCPProvider.mount_volume functionality."""

    @pytest.fixture
    def provider(self):
        """Create a mock FCP provider."""
        provider = Mock(spec=FCPProvider)
        provider.fcp_config = Mock(region="us-central1-b")
        provider.http = Mock()
        provider.is_volume_id = FCPProvider.is_volume_id.__get__(provider)
        provider._get_project_id = Mock(return_value="proj_test123")
        return provider

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return Task(
            task_id="task_abc123",
            name="test-task",
            status=TaskStatus.RUNNING,
            created_at=datetime.now(timezone.utc),
            instance_type="a100-80gb",
            num_instances=1,
            cost_per_hour="$10.00",
            region="us-central1-b",
            instances=["inst_123", "inst_456"],
            ssh_host="1.2.3.4",
            ssh_port=22,
        )

    @pytest.fixture
    def sample_volume(self):
        """Create a sample volume."""
        return Volume(
            volume_id="vol_xyz789",
            name="test-volume",
            size_gb=100,
            region="us-central1-b",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now(timezone.utc),
            attached_to=[],
        )

    def test_mount_volume_success(self, provider, sample_task, sample_volume):
        """Test successful volume mount."""
        # Setup mocks
        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        # Mock bid response
        bid_response = [{"fid": "task_abc123", "launch_specification": {"volumes": []}}]
        provider.http.request = Mock(
            side_effect=[
                bid_response,  # GET /v2/spot/bids
                None,  # PATCH /v2/spot/bids/{task_id}
            ]
        )

        # Mock remote operations
        with patch("flow.providers.fcp.provider.FCPRemoteOperations") as mock_remote_ops_class:
            mock_remote_ops = Mock()
            mock_remote_ops.execute_command = Mock(return_value="")
            mock_remote_ops_class.return_value = mock_remote_ops

            # Call the actual method
            FCPProvider.mount_volume(provider, "vol_xyz789", "task_abc123")

        # Verify API calls
        assert provider.get_task.called_with("task_abc123")
        assert provider.list_volumes.called

        # Verify PATCH request
        patch_call = provider.http.request.call_args_list[1]
        assert patch_call[1]["method"] == "PATCH"
        assert patch_call[1]["url"] == "/v2/spot/bids/task_abc123"
        assert patch_call[1]["json"]["launch_specification"]["volumes"] == ["vol_xyz789"]

        # Verify SSH mount command
        mock_remote_ops.execute_command.assert_called_once()
        mount_cmd = mock_remote_ops.execute_command.call_args[0][1]
        assert "sudo mkdir -p /mnt/test-volume" in mount_cmd
        assert "sudo mount /dev/vdd /mnt/test-volume" in mount_cmd

    def test_mount_volume_by_name(self, provider, sample_task, sample_volume):
        """Test mounting volume by name instead of ID."""
        # Setup mocks
        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        # Mock bid response
        bid_response = [{"fid": "task_abc123", "launch_specification": {"volumes": []}}]
        provider.http.request = Mock(
            side_effect=[
                bid_response,  # GET /v2/spot/bids
                None,  # PATCH /v2/spot/bids/{task_id}
            ]
        )

        with patch("flow.providers.fcp.provider.FCPRemoteOperations"):
            # Call with volume name instead of ID
            FCPProvider.mount_volume(provider, "test-volume", "task_abc123")

        # Should resolve to the correct volume ID
        patch_call = provider.http.request.call_args_list[1]
        assert patch_call[1]["json"]["launch_specification"]["volumes"] == ["vol_xyz789"]

    def test_mount_volume_task_not_found(self, provider):
        """Test mounting to non-existent task."""
        provider.get_task = Mock(return_value=None)

        with pytest.raises(TaskNotFoundError) as exc_info:
            FCPProvider.mount_volume(provider, "vol_xyz789", "task_notfound")

        assert "Task 'task_notfound' not found" in str(exc_info.value)

    def test_mount_volume_not_found(self, provider, sample_task):
        """Test mounting non-existent volume."""
        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[])  # No volumes

        with pytest.raises(ResourceNotFoundError) as exc_info:
            FCPProvider.mount_volume(provider, "vol_notfound", "task_abc123")

        assert "Volume 'vol_notfound' not found" in str(exc_info.value)

    def test_mount_volume_region_mismatch(self, provider, sample_task, sample_volume):
        """Test mounting volume from different region."""
        # Set different regions
        sample_volume.region = "eu-central1-a"

        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        with pytest.raises(ValidationError) as exc_info:
            FCPProvider.mount_volume(provider, "vol_xyz789", "task_abc123")

        assert "Region mismatch" in str(exc_info.value)
        assert "us-central1-b" in str(exc_info.value)
        assert "eu-central1-a" in str(exc_info.value)

    def test_mount_volume_already_attached(self, provider, sample_task, sample_volume):
        """Test mounting already attached volume."""
        # Volume already attached to one of the task's instances
        sample_volume.attached_to = ["inst_123"]

        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        with pytest.raises(ValidationError) as exc_info:
            FCPProvider.mount_volume(provider, "vol_xyz789", "task_abc123")

        assert "already attached to this task" in str(exc_info.value)

    def test_mount_volume_api_failure(self, provider, sample_task, sample_volume):
        """Test handling of API update failure."""
        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        # Mock bid response and API failure
        bid_response = [{"fid": "task_abc123", "launch_specification": {"volumes": []}}]
        provider.http.request = Mock(
            side_effect=[
                bid_response,  # GET /v2/spot/bids
                Exception("API Error"),  # PATCH fails
            ]
        )

        with pytest.raises(FCPAPIError) as exc_info:
            FCPProvider.mount_volume(provider, "vol_xyz789", "task_abc123")

        assert "Failed to update bid volumes" in str(exc_info.value)

    def test_mount_volume_ssh_failure_with_rollback(self, provider, sample_task, sample_volume):
        """Test SSH failure triggers rollback."""
        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        # Mock successful API update but SSH failure
        bid_response = [
            {
                "fid": "task_abc123",
                "launch_specification": {"volumes": ["vol_old"]},  # Existing volume
            }
        ]
        provider.http.request = Mock(
            side_effect=[
                bid_response,  # GET /v2/spot/bids
                None,  # PATCH succeeds
                None,  # Rollback PATCH
            ]
        )

        with patch("flow.providers.fcp.provider.FCPRemoteOperations") as mock_remote_ops_class:
            mock_remote_ops = Mock()
            mock_remote_ops.execute_command = Mock(side_effect=Exception("SSH connection failed"))
            mock_remote_ops_class.return_value = mock_remote_ops

            with pytest.raises(RemoteExecutionError) as exc_info:
                FCPProvider.mount_volume(provider, "vol_xyz789", "task_abc123")

        assert "Failed to mount volume" in str(exc_info.value)

        # Verify rollback was attempted
        rollback_call = provider.http.request.call_args_list[2]
        assert rollback_call[1]["method"] == "PATCH"
        assert rollback_call[1]["json"]["launch_specification"]["volumes"] == ["vol_old"]

    def test_mount_volume_multiple_volumes(self, provider, sample_task, sample_volume):
        """Test mounting when task already has volumes."""
        provider.get_task = Mock(return_value=sample_task)
        provider.list_volumes = Mock(return_value=[sample_volume])

        # Task already has 2 volumes
        bid_response = [
            {"fid": "task_abc123", "launch_specification": {"volumes": ["vol_001", "vol_002"]}}
        ]
        provider.http.request = Mock(
            side_effect=[
                bid_response,  # GET /v2/spot/bids
                None,  # PATCH
            ]
        )

        with patch("flow.providers.fcp.provider.FCPRemoteOperations") as mock_remote_ops_class:
            mock_remote_ops = Mock()
            mock_remote_ops.execute_command = Mock(return_value="")
            mock_remote_ops_class.return_value = mock_remote_ops

            FCPProvider.mount_volume(provider, "vol_xyz789", "task_abc123")

        # Verify it adds to existing volumes
        patch_call = provider.http.request.call_args_list[1]
        assert patch_call[1]["json"]["launch_specification"]["volumes"] == [
            "vol_001",
            "vol_002",
            "vol_xyz789",
        ]

        # Verify correct device letter (third volume = /dev/vdf)
        mount_cmd = mock_remote_ops.execute_command.call_args[0][1]
        assert "sudo mount /dev/vdf /mnt/test-volume" in mount_cmd
