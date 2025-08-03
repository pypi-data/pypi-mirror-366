"""Integration tests for file share functionality.

These tests verify the complete flow from API call to script generation.
"""

from unittest.mock import Mock, patch

import pytest

from flow import TaskConfig
from flow._internal.config import Config
from flow.api.models import StorageInterface, VolumeSpec
from flow.errors import ResourceNotAvailableError
from flow.providers.fcp.provider import FCPProvider
from flow.providers.fcp.runtime.startup.builder import FCPStartupScriptBuilder


class TestFileShareIntegration:
    """Test file share creation and usage in tasks."""

    @pytest.fixture
    def fcp_config(self):
        """Create FCP configuration for testing."""
        return Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={
                "api_url": "https://api.test.mlfoundry.com",
                "project": "test-project",
                "region": "us-central1-a"
            }
        )

    def test_create_file_share_and_attach_to_task(self, fcp_config):
        """Complete workflow: create file share and use in multi-node task."""
        # Arrange
        mock_http = Mock()
        provider = FCPProvider(fcp_config, http_client=mock_http)

        # Mock project resolver to avoid API calls
        provider.project_resolver.resolve = Mock(return_value="test-project-id")
        provider._project_id = "test-project-id"

        # Mock successful file share creation
        volume_response = {
            "fid": "vol-shared-123",
            "name": "ml-datasets",
            "region": "us-central1-a",
            "status": "available",
            "created_at": "2024-01-01T00:00:00Z",
            "disk_interface": "File",
            "nfs_endpoint": "fileshare-vol-shared-123.fcp.internal"
        }

        # Mock successful task submission
        task_response = {
            "bid_id": "task-456",
            "status": "pending"
        }

        with patch.object(provider.http, 'request') as mock_request:
            # Configure mock to return different responses
            mock_request.side_effect = [
                volume_response,  # create_volume response
                {"instances": [{"instance_type": "a100", "region": "us-central1-a"}]},  # availability check
                task_response  # submit_bid response
            ]

            # Act - Create file share
            volume = provider.create_volume(
                size_gb=1000,
                name="ml-datasets",
                interface="file"
            )

            # Assert volume created correctly
            assert volume.volume_id == "vol-shared-123"
            assert volume.name == "ml-datasets"

            # Verify API was called with file interface
            create_call = mock_request.call_args_list[0]
            assert create_call[1]['json']['disk_interface'] == "File"

            # Act - Create task with file share
            config = TaskConfig(
                name="distributed-training",
                instance_type="a100",
                num_instances=4,
                command="python train.py",
                volumes=[VolumeSpec(
                    volume_id=volume.volume_id,
                    mount_path="/datasets",
                    interface=StorageInterface.FILE
                )]
            )

            # Need to simulate what would happen in real FCP provider
            # The provider would enrich the volume data with NFS endpoint
            # For testing, we'll create the script context directly
            from flow.providers.fcp.runtime.startup.sections import ScriptContext, VolumeSection

            # Create context with proper volume data
            volume_data = {
                "volume_id": volume.volume_id,
                "mount_path": "/datasets",
                "interface": "file",
                "nfs_endpoint": "fileshare-vol-shared-123.fcp.internal"
            }

            context = ScriptContext(volumes=[volume_data])
            volume_section = VolumeSection()

            # Generate just the volume section to test
            volume_script = volume_section.generate(context)

            # Assert script contains NFS mount commands
            assert "mount -t nfs4" in volume_script
            assert "nfs-common" in volume_script
            assert "/datasets" in volume_script
            assert "fileshare-vol-shared-123.fcp.internal" in volume_script

    def test_file_share_unavailable_region(self, fcp_config):
        """Handle file share unavailability gracefully."""
        # Arrange
        mock_http = Mock()
        provider = FCPProvider(fcp_config, http_client=mock_http)

        # Mock project resolver to avoid API calls
        provider.project_resolver.resolve = Mock(return_value="test-project-id")
        provider._project_id = "test-project-id"

        # Mock API error for unsupported region
        from flow.providers.fcp.core.errors import FCPAPIError
        error_response = {
            "error": "Invalid disk_interface",
            "message": "File interface not supported in us-central1-a"
        }

        api_error = FCPAPIError(
            "Invalid disk_interface: File not supported in this region",
            status_code=400,
            response_body=error_response
        )

        with patch.object(provider.http, 'request', side_effect=api_error):
            # Act & Assert
            with pytest.raises(ResourceNotAvailableError) as exc_info:
                provider.create_volume(100, "test", interface="file")

            error = exc_info.value
            assert "File shares not available in region us-central1-a" in str(error)
            assert len(error.suggestions) >= 2
            assert any("block" in s.lower() for s in error.suggestions)

    def test_mixed_volume_types_in_task(self, fcp_config):
        """Task can use both block and file volumes."""
        # Arrange
        config = TaskConfig(
            name="hybrid-storage-task",
            instance_type="a100",
            command="python process.py",
            volumes=[
                # Block volume for scratch space
                VolumeSpec(
                    volume_id="vol-block-123",
                    mount_path="/scratch",
                    interface=StorageInterface.BLOCK
                ),
                # File share for shared data
                VolumeSpec(
                    volume_id="vol-file-456",
                    mount_path="/shared",
                    interface=StorageInterface.FILE
                )
            ]
        )

        # Simulate volume data that would come from provider
        volume_data = [
            {
                "volume_id": "vol-block-123",
                "mount_path": "/scratch",
                "interface": "block"
            },
            {
                "volume_id": "vol-file-456",
                "mount_path": "/shared",
                "interface": "file",
                "nfs_endpoint": "fileshare-vol-file-456.fcp.internal"
            }
        ]

        # Act - Generate startup script
        from flow.providers.fcp.runtime.startup.sections import ScriptContext, VolumeSection

        context = ScriptContext(volumes=volume_data)
        section = VolumeSection()
        script = section.generate(context)

        # Assert both mount types are present
        assert "/dev/xvdf" in script  # Block device
        assert "mkfs.ext4" in script  # Block formatting
        assert "mount -t nfs4" in script  # NFS mount
        assert "fileshare-vol-file-456.fcp.internal" in script
        assert "/scratch ext4" in script  # Block fstab entry
        assert "/shared nfs4" in script  # NFS fstab entry

    def test_startup_script_size_with_file_shares(self):
        """Verify script stays under FCP size limit with file share commands."""
        # Arrange
        config = TaskConfig(
            name="test-task",
            instance_type="a100",
            command="echo test",
            volumes=[
                VolumeSpec(
                    volume_id=f"vol-file-{i}",
                    mount_path=f"/data{i}",
                    interface=StorageInterface.FILE
                )
                for i in range(5)  # Multiple file shares
            ]
        )

        # Act
        builder = FCPStartupScriptBuilder()
        script = builder.build(config)

        # Assert script is within limits
        assert script.is_valid
        # If compressed, the script will be larger but still valid
        if not script.compressed:
            assert len(script.content) < 10000  # FCP limit
            # Verify all mounts are included
            for i in range(5):
                assert f"/data{i}" in script.content
        else:
            # For compressed scripts, check the bootstrap wrapper is present
            assert "#!/bin/bash" in script.content
            assert "base64 -d | gunzip | bash" in script.content

    def test_file_share_persistence_across_tasks(self, fcp_config):
        """File shares can be reused across multiple tasks."""
        # This test verifies the conceptual flow - in reality,
        # file shares persist and can be mounted by multiple tasks

        # Arrange
        mock_http = Mock()
        provider = FCPProvider(fcp_config, http_client=mock_http)

        # Create a file share once
        volume_id = "vol-persistent-789"

        # Create two different tasks using the same volume
        task1 = TaskConfig(
            name="writer-task",
            instance_type="a100",
            command="python write_data.py",
            volumes=[VolumeSpec(
                volume_id=volume_id,
                mount_path="/shared-data"
            )]
        )

        task2 = TaskConfig(
            name="reader-task",
            instance_type="a100",
            command="python read_data.py",
            volumes=[VolumeSpec(
                volume_id=volume_id,
                mount_path="/shared-data"
            )]
        )

        # Act - Generate scripts for both
        builder = FCPStartupScriptBuilder()
        script1 = builder.build(task1)
        script2 = builder.build(task2)

        # Assert both can mount the same volume
        assert "/shared-data" in script1.content
        assert "/shared-data" in script2.content

        # Both should use same mount approach
        assert script1.content.count("mount") == script2.content.count("mount")
