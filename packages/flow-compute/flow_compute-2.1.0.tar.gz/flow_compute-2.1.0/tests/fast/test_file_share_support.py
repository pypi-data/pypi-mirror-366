"""Unit tests for file share support functionality."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from flow._internal.config import Config
from flow.api.client import Flow
from flow.api.models import StorageInterface, Volume
from flow.errors import ResourceNotAvailableError
from flow.providers.fcp.core.errors import FCPAPIError
from flow.providers.fcp.provider import FCPProvider


class TestFlowCreateVolume:
    """Test Flow.create_volume with file share support."""

    def test_create_block_volume_default(self):
        """Default behavior creates block storage."""
        # Arrange
        mock_provider = Mock()
        mock_provider.create_volume.return_value = Volume(
            volume_id="vol-123",
            name="test-vol",
            size_gb=100,
            region="us-central1-a",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now(timezone.utc)
        )

        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        flow = Flow(config=config)
        flow._provider = mock_provider

        # Act
        volume = flow.create_volume(100, "test-vol")

        # Assert
        assert volume.interface == StorageInterface.BLOCK
        mock_provider.create_volume.assert_called_once_with(100, "test-vol", "block")

    def test_create_file_share_explicit(self):
        """Can create file share with interface='file'."""
        # Arrange
        mock_provider = Mock()
        mock_provider.create_volume.return_value = Volume(
            volume_id="vol-456",
            name="shared-data",
            size_gb=200,
            region="us-central1-a",
            interface=StorageInterface.FILE,
            created_at=datetime.now(timezone.utc)
        )

        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        flow = Flow(config=config)
        flow._provider = mock_provider

        # Act
        volume = flow.create_volume(200, "shared-data", interface="file")

        # Assert
        assert volume.interface == StorageInterface.FILE
        mock_provider.create_volume.assert_called_once_with(200, "shared-data", "file")

    def test_invalid_interface_rejected(self):
        """Invalid interface parameter raises ValueError."""
        # Arrange
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        flow = Flow(config=config)
        flow._provider = Mock()

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            flow.create_volume(100, "test", interface="invalid")

        assert "Invalid interface: invalid" in str(exc_info.value)
        assert "Must be 'block' or 'file'" in str(exc_info.value)
        flow._provider.create_volume.assert_not_called()

    def test_provider_unavailable_error_propagated(self):
        """ResourceNotAvailableError from provider is propagated."""
        # Arrange
        mock_provider = Mock()
        mock_provider.create_volume.side_effect = ResourceNotAvailableError(
            "File shares not available in region us-east1-a",
            suggestions=["Use block storage", "Try us-central1-a"]
        )

        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        flow = Flow(config=config)
        flow._provider = mock_provider

        # Act & Assert
        with pytest.raises(ResourceNotAvailableError) as exc_info:
            flow.create_volume(100, "test", interface="file")

        assert "File shares not available" in str(exc_info.value)
        assert exc_info.value.suggestions == ["Use block storage", "Try us-central1-a"]


class TestFCPProviderFileShare:
    """Test FCP provider file share implementation."""

    def test_block_storage_uses_correct_constant(self):
        """Block storage uses DISK_INTERFACE_BLOCK."""
        # Arrange
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)

        mock_response = {
            "fid": "vol-123",
            "name": "test-vol",
            "region": "us-central1-a",
            "status": "available",
            "created_at": "2024-01-01T00:00:00Z"
        }

        # Mock project resolver to avoid API calls during init
        provider.project_resolver.resolve = Mock(return_value="test-project-id")
        provider._project_id = "test-project-id"

        with patch.object(provider.http, 'request', return_value=mock_response) as mock_request:
            # Act
            volume = provider.create_volume(100, "test-vol", interface="block")

            # Assert
            assert volume.volume_id == "vol-123"
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['json']['disk_interface'] == "Block"

    def test_file_share_uses_correct_constant(self):
        """File share uses DISK_INTERFACE_FILE."""
        # Arrange
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)

        mock_response = {
            "fid": "vol-456",
            "name": "shared-vol",
            "region": "us-central1-a",
            "status": "available",
            "created_at": "2024-01-01T00:00:00Z"
        }

        # Mock project resolver to avoid API calls during init
        provider.project_resolver.resolve = Mock(return_value="test-project-id")
        provider._project_id = "test-project-id"

        with patch.object(provider.http, 'request', return_value=mock_response) as mock_request:
            # Act
            volume = provider.create_volume(200, "shared-vol", interface="file")

            # Assert
            assert volume.volume_id == "vol-456"
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['json']['disk_interface'] == "File"

    def test_file_share_unavailable_error_handling(self):
        """400 error for file shares provides helpful message."""
        # Arrange
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project", "region": "us-east1-a"}
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)

        # Simulate API rejecting file share creation
        api_error = FCPAPIError(
            "Invalid disk_interface: File not supported in this region",
            status_code=400,
            response_body={"error": "Invalid disk_interface"}
        )

        # Mock project resolver to avoid API calls during init
        provider.project_resolver.resolve = Mock(return_value="test-project-id")
        provider._project_id = "test-project-id"

        with patch.object(provider.http, 'request', side_effect=api_error):
            # Act & Assert
            with pytest.raises(ResourceNotAvailableError) as exc_info:
                provider.create_volume(100, "test", interface="file")

            error = exc_info.value
            assert "File shares not available in region us-east1-a" in str(error)
            assert "Use block storage: interface='block'" in error.suggestions
            assert "docs.mlfoundry.com/regions" in error.suggestions[1]

    def test_other_errors_not_transformed(self):
        """Non-file-share 400 errors are not transformed."""
        # Arrange
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)

        # Different 400 error
        api_error = FCPAPIError(
            "Invalid size_gb: must be positive",
            status_code=400,
            response_body={"error": "Invalid size_gb"}
        )

        # Mock project resolver to avoid API calls during init
        provider.project_resolver.resolve = Mock(return_value="test-project-id")
        provider._project_id = "test-project-id"

        with patch.object(provider.http, 'request', side_effect=api_error):
            # Act & Assert
            with pytest.raises(FCPAPIError) as exc_info:
                provider.create_volume(-1, "test", interface="block")

            # Original error is raised, not transformed
            assert exc_info.value is api_error


class TestVolumeScriptGeneration:
    """Test startup script generation for volumes."""

    def test_block_volume_generates_device_mount(self):
        """Block volumes generate traditional device mount commands."""
        from flow.providers.fcp.runtime.startup.sections import ScriptContext, VolumeSection

        # Arrange
        section = VolumeSection()
        context = ScriptContext(
            volumes=[{
                "volume_id": "vol-123",
                "mount_path": "/data",
                "interface": "block"
            }]
        )

        # Act
        script = section.generate(context)

        # Assert
        assert "/dev/xvdf" in script
        assert "mkfs.ext4" in script
        assert 'mount "$DEVICE" /data' in script
        assert "ext4 defaults,nofail" in script

    def test_file_share_generates_nfs_mount(self):
        """File shares generate NFS mount commands."""
        from flow.providers.fcp.runtime.startup.sections import ScriptContext, VolumeSection

        # Arrange
        section = VolumeSection()
        context = ScriptContext(
            volumes=[{
                "volume_id": "vol-456",
                "mount_path": "/shared",
                "interface": "file",
                "nfs_endpoint": "fileshare-vol-456.fcp.internal"
            }]
        )

        # Act
        script = section.generate(context)

        # Assert
        assert "mount -t nfs4" in script
        assert "fileshare-vol-456.fcp.internal" in script
        assert "nfsvers=4.1" in script
        assert "apt-get install -y -qq nfs-common" in script
        assert "/shared nfs4" in script  # fstab entry

    def test_mixed_volumes_handled_correctly(self):
        """Mixed block and file volumes are handled correctly."""
        from flow.providers.fcp.runtime.startup.sections import ScriptContext, VolumeSection

        # Arrange
        section = VolumeSection()
        context = ScriptContext(
            volumes=[
                {
                    "volume_id": "vol-123",
                    "mount_path": "/data1",
                    "interface": "block"
                },
                {
                    "volume_id": "vol-456",
                    "mount_path": "/shared",
                    "interface": "file",
                    "nfs_endpoint": "fileshare-vol-456.fcp.internal"
                }
            ]
        )

        # Act
        script = section.generate(context)

        # Assert
        # Block volume commands
        assert "/dev/xvdf" in script
        assert "mkfs.ext4" in script

        # File share commands
        assert "mount -t nfs4" in script
        assert "nfs-common" in script

        # Verification includes both types
        assert 'mount | grep -E "(^/dev/xvd[f-z]|type nfs)"' in script

    def test_default_interface_treated_as_block(self):
        """Volumes without interface specified are treated as block."""
        from flow.providers.fcp.runtime.startup.sections import ScriptContext, VolumeSection

        # Arrange
        section = VolumeSection()
        context = ScriptContext(
            volumes=[{
                "volume_id": "vol-789",
                "mount_path": "/data"
                # No interface specified
            }]
        )

        # Act
        script = section.generate(context)

        # Assert
        assert "/dev/xvdf" in script
        assert "mkfs.ext4" in script
        # The grep pattern contains 'nfs' but no actual NFS commands should be present
        assert "mount -t nfs" not in script  # No NFS mount commands
        assert "nfs-common" not in script  # No NFS packages


class TestEndToEndScenarios:
    """Test complete user scenarios."""

    @patch('flow.providers.factory.create_provider')
    def test_create_file_share_for_multinode_training(self, mock_create_provider):
        """User creates file share for distributed training scenario."""
        # Arrange
        mock_provider = Mock()
        mock_create_provider.return_value = mock_provider

        # Simulate successful file share creation
        mock_provider.create_volume.return_value = Volume(
            volume_id="vol-shared-123",
            name="training-dataset",
            size_gb=500,
            region="us-central1-a",
            interface=StorageInterface.FILE,
            created_at=datetime.now(timezone.utc)
        )

        # Act
        # Create Flow with mocked provider
        flow = Flow(config=Config(
            provider="test",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        ))
        flow._provider = mock_provider
        volume = flow.create_volume(
            size_gb=500,
            name="training-dataset",
            interface="file"
        )

        # Assert
        assert volume.interface == StorageInterface.FILE
        assert volume.name == "training-dataset"
        assert volume.size_gb == 500

        # Verify provider was called correctly
        mock_provider.create_volume.assert_called_once_with(
            500, "training-dataset", "file"
        )

    @patch('flow.providers.factory.create_provider')
    def test_fallback_to_block_storage(self, mock_create_provider):
        """User handles unavailable file share by using block storage."""
        # Arrange
        mock_provider = Mock()
        mock_create_provider.return_value = mock_provider

        # First attempt fails
        mock_provider.create_volume.side_effect = [
            ResourceNotAvailableError(
                "File shares not available in region us-east1-a",
                suggestions=["Use block storage", "Try us-central1-a"]
            ),
            # Second attempt succeeds with block storage
            Volume(
                volume_id="vol-block-456",
                name="training-dataset",
                size_gb=500,
                region="us-east1-a",
                interface=StorageInterface.BLOCK,
                created_at=datetime.now(timezone.utc)
            )
        ]

        # Create Flow with mocked provider
        flow = Flow(config=Config(
            provider="test",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        ))
        flow._provider = mock_provider

        # Act - First try file share
        with pytest.raises(ResourceNotAvailableError):
            flow.create_volume(500, "training-dataset", interface="file")

        # Act - Fallback to block
        volume = flow.create_volume(500, "training-dataset", interface="block")

        # Assert
        assert volume.interface == StorageInterface.BLOCK
        assert mock_provider.create_volume.call_count == 2
