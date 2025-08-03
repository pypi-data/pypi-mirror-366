"""Comprehensive unit tests for volume CLI commands."""

from contextlib import contextmanager
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from flow._internal.config import Config
from flow.api.models import StorageInterface, Volume
from flow.cli.app import cli
from flow.errors import FlowError


def create_mock_flow():
    """Create a properly mocked Flow instance."""
    mock_flow = Mock()
    # Add any default mock behaviors here
    return mock_flow


@contextmanager
def mock_flow_init():
    """Context manager to mock Flow initialization."""
    mock_config = MagicMock(spec=Config)
    mock_config.auth_token = "test-token"
    mock_config.api_url = "https://api.test.com"
    mock_config.project = "test-project"

    with patch('flow._internal.config.Config.from_env', return_value=mock_config):
        yield



class TestVolumeListCommand:
    """Test the 'flow volumes list' command."""

    def test_list_empty_volumes(self):
        """When no volumes exist, show appropriate message."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        mock_flow.list_volumes.return_value = []

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'list'])

        # Assert
        assert result.exit_code == 0
        assert "No volumes found" in result.output
        mock_flow.list_volumes.assert_called_once()

    def test_list_single_volume_with_all_fields(self):
        """Display single volume with all fields properly."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volume = Volume(
            volume_id="vol_abc123",
            name="test-volume",
            size_gb=100,
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        mock_flow.list_volumes.return_value = [volume]

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'list'])

        # Assert
        assert result.exit_code == 0
        assert "vol_abc123" in result.output
        assert "test-volume" in result.output
        assert "100" in result.output
        assert "2024-01-01 12:00" in result.output

    def test_list_volume_without_name(self):
        """Handle volumes with empty names gracefully."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volume = Volume(
            volume_id="vol_xyz789",
            name="",  # Empty name
            size_gb=50,
            region="us-west-2",
            interface=StorageInterface.BLOCK,
            created_at=datetime(2024, 1, 1, 12, 0, 0)
        )
        mock_flow.list_volumes.return_value = [volume]

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'list'])

        # Assert
        assert result.exit_code == 0
        assert "vol_xyz789" in result.output
        assert "-" in result.output  # Empty name shows as "-"

    def test_list_multiple_volumes(self):
        """Display multiple volumes in table format."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"volume-{i}",
                size_gb=100 * (i + 1),
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime(2024, 1, i, 12, 0, 0)
            )
            for i in range(1, 4)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'list'])

        # Assert
        assert result.exit_code == 0
        assert "vol_001" in result.output
        assert "vol_002" in result.output
        assert "vol_003" in result.output
        assert "volume-1" in result.output
        assert "volume-2" in result.output
        assert "volume-3" in result.output

    def test_list_api_error_handling(self):
        """Handle API errors gracefully."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        mock_flow.list_volumes.side_effect = FlowError("API connection failed")

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'list'])

        # Assert
        # CLI handles errors via handle_error() which prints and exits
        assert result.exit_code == 1
        assert "API connection failed" in result.output


class TestVolumeCreateCommand:
    """Test the 'flow volumes create' command."""

    def test_create_basic_volume(self):
        """Create volume with size only."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        created_volume = Volume(
            volume_id="vol_new123",
            name="flow-data",  # Auto-generated name
            size_gb=200,
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now()
        )
        mock_flow.create_volume.return_value = created_volume

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'create', '--size', '200'])

        # Assert
        assert result.exit_code == 0
        assert "✓ Volume created: vol_new123" in result.output
        mock_flow.create_volume.assert_called_once_with(size_gb=200, name=None)

    def test_create_named_volume(self):
        """Create volume with custom name."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        created_volume = Volume(
            volume_id="vol_custom456",
            name="my-datasets",
            size_gb=500,
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now()
        )
        mock_flow.create_volume.return_value = created_volume

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'create', '--size', '500', '--name', 'my-datasets'])

        # Assert
        assert result.exit_code == 0
        assert "✓ Volume created: vol_custom456" in result.output
        mock_flow.create_volume.assert_called_once_with(size_gb=500, name='my-datasets')

    def test_create_missing_required_size(self):
        """Fail when size parameter is missing."""
        # Arrange
        runner = CliRunner()

        # Act
        result = runner.invoke(cli, ['volumes', 'create'])

        # Assert
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_create_validation_error(self):
        """Handle validation errors from API."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        mock_flow.create_volume.side_effect = Exception("Invalid size: must be between 1 and 16000 GB")

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'create', '--size', '20000'])

        # Assert
        assert result.exit_code != 0
        assert "Invalid size" in result.output

    def test_create_quota_exceeded_error(self):
        """Handle quota errors gracefully."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        mock_flow.create_volume.side_effect = Exception("Quota exceeded: maximum 50TB per project")

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'create', '--size', '1000'])

        # Assert
        assert result.exit_code != 0
        assert "Quota exceeded" in result.output


class TestVolumeDeleteCommand:
    """Test the 'flow volumes delete' command."""

    def test_delete_with_confirmation(self):
        """Delete requires confirmation by default."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete', 'vol_123'], input='y\n')

        # Assert
        assert result.exit_code == 0
        assert "Delete volume vol_123?" in result.output
        assert "✓ Volume vol_123 deleted" in result.output
        mock_flow.delete_volume.assert_called_once_with('vol_123')

    def test_delete_skip_confirmation(self):
        """Delete with --yes skips confirmation."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete', 'vol_456', '--yes'])

        # Assert
        assert result.exit_code == 0
        assert "Delete volume" not in result.output  # No confirmation prompt
        assert "✓ Volume vol_456 deleted" in result.output
        mock_flow.delete_volume.assert_called_once_with('vol_456')

    def test_delete_user_cancels(self):
        """User can cancel deletion."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete', 'vol_789'], input='n\n')

        # Assert
        assert result.exit_code == 0
        assert "Delete volume" in result.output
        assert "Cancelled" in result.output
        mock_flow.delete_volume.assert_not_called()

    def test_delete_nonexistent_volume(self):
        """Handle deletion of non-existent volume."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        mock_flow.delete_volume.side_effect = Exception("Volume not found: vol_missing")

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete', 'vol_missing', '--yes'])

        # Assert
        assert result.exit_code != 0
        assert "Volume not found" in result.output


class TestVolumeDeleteAllCommand:
    """Test the 'flow volumes delete-all' command."""

    def test_delete_all_basic(self):
        """Delete all volumes with confirmation."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"test-volume-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(5)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all'], input='y\n')

        # Assert
        assert result.exit_code == 0
        assert "Found 5 volume(s) to delete" in result.output
        assert "Delete 5 volume(s)?" in result.output
        assert "Deleted 5 volume(s)" in result.output
        assert mock_flow.delete_volume.call_count == 5

    def test_delete_all_with_pattern(self):
        """Delete only volumes matching pattern."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"{'test' if i < 3 else 'prod'}-volume-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(5)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--pattern', 'test-', '--yes'])

        # Assert
        assert result.exit_code == 0
        assert "Found 3 volume(s) to delete" in result.output
        assert "Deleted 3 volume(s)" in result.output
        assert mock_flow.delete_volume.call_count == 3
        # Verify only test volumes were deleted
        deleted_ids = [call[0][0] for call in mock_flow.delete_volume.call_args_list]
        assert all(vid in ['vol_000', 'vol_001', 'vol_002'] for vid in deleted_ids)

    def test_delete_all_dry_run(self):
        """Dry run shows what would be deleted without deleting."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"volume-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(3)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--dry-run'])

        # Assert
        assert result.exit_code == 0
        assert "Found 3 volume(s) to delete" in result.output
        assert "vol_000 (volume-0)" in result.output
        assert "vol_001 (volume-1)" in result.output
        assert "vol_002 (volume-2)" in result.output
        assert "Dry run - no volumes deleted" in result.output
        mock_flow.delete_volume.assert_not_called()

    def test_delete_all_handles_unnamed_volumes(self):
        """Handle volumes without names gracefully."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id="vol_unnamed",
                name="",  # Empty name
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
        ]
        mock_flow.list_volumes.return_value = volumes

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])

        # Assert
        assert result.exit_code == 0
        assert "vol_unnamed" in result.output
        assert "Deleted 1 volume(s)" in result.output

    def test_delete_all_partial_failures(self):
        """Handle partial failures gracefully."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=f"volume-{i}",
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i in range(5)
        ]
        mock_flow.list_volumes.return_value = volumes

        # Make some deletions fail
        def delete_side_effect(volume_id):
            if volume_id in ['vol_001', 'vol_003']:
                raise Exception(f"Cannot delete attached volume: {volume_id}")
            return None

        mock_flow.delete_volume.side_effect = delete_side_effect

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all', '--yes'])

        # Assert
        assert result.exit_code == 0
        assert "Deleted 3 volume(s)" in result.output
        assert "Failed to delete 2 volume(s)" in result.output
        assert "Failed to delete vol_001: Cannot delete attached volume" in result.output

    def test_delete_all_no_volumes_found(self):
        """Handle case when no volumes match criteria."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        mock_flow.list_volumes.return_value = []

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all'])

        # Assert
        assert result.exit_code == 0
        assert "No volumes found" in result.output

    def test_delete_all_complex_regex_patterns(self):
        """Test complex regex patterns for real-world scenarios."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [
            Volume(
                volume_id=f"vol_{i:03d}",
                name=name,
                size_gb=100,
                region="us-east-1",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now()
            )
            for i, name in enumerate([
                "inttest-volume-20240101-120000-abc123",
                "inttest-volume-20240102-140000-def456",
                "production-data-v1",
                "backup-2024-01-01",
                "experiment-xyz789"
            ])
        ]
        mock_flow.list_volumes.return_value = volumes

        # Act - Delete only integration test volumes
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(
                cli,
                ['volumes', 'delete-all', '--pattern', 'inttest-volume-', '--yes']
            )

        # Assert
        assert result.exit_code == 0
        assert "Found 2 volume(s) to delete" in result.output
        assert mock_flow.delete_volume.call_count == 2

    def test_delete_all_user_cancels(self):
        """User can cancel bulk deletion."""
        # Arrange
        runner = CliRunner()
        mock_flow = Mock()
        volumes = [Volume(
            volume_id=f"vol_{i:03d}",
            name=f"volume-{i}",
            size_gb=100,
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now()
        ) for i in range(10)]
        mock_flow.list_volumes.return_value = volumes

        # Act
        with mock_flow_init(), patch('flow.cli.commands.volumes.Flow', return_value=mock_flow):
            result = runner.invoke(cli, ['volumes', 'delete-all'], input='n\n')

        # Assert
        assert result.exit_code == 0
        assert "Delete 10 volume(s)?" in result.output
        assert "Cancelled" in result.output
        mock_flow.delete_volume.assert_not_called()
