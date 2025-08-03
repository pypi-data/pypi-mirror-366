"""Integration tests for Flow mount functionality."""

from unittest.mock import Mock, patch

import pytest

from flow import Flow
from flow._internal.config import Config
from flow.api.models import MountSpec, Task, TaskConfig, TaskStatus


class TestFlowMounts:
    """Test Flow.run() with mounts parameter."""

    @pytest.fixture
    def mock_provider(self):
        """Create mock provider for testing."""
        provider = Mock()
        provider.prepare_task_config = Mock(side_effect=lambda x: x)
        provider.find_instances = Mock(return_value=[{
            "instance_type": "a100-80gb",
            "price_per_hour": 5.0,
            "gpu_count": 1
        }])
        provider.submit_task = Mock(return_value=Task(
            task_id="task-123",
            name="test-task",
            status=TaskStatus.PENDING,
            instance_type="a100-80gb",
            region="us-east-1",
            created_at=1234567890,
            num_instances=1,
            cost_per_hour="$5.00"
        ))
        return provider

    @pytest.fixture
    def flow_client(self, mock_provider):
        """Create Flow client with mocked provider."""
        config = Config(
            provider="fcp",
            auth_token="test-token"
        )

        with patch('flow.api.client.create_provider', return_value=mock_provider):
            client = Flow(config)
            yield client

    def test_run_with_single_mount_string(self, flow_client, mock_provider):
        """Test run with single mount as string."""
        task_config = TaskConfig(
            name="test",
            instance_type="a100",
            command="echo test"
        )

        # Run with single S3 mount
        task = flow_client.run(task_config, mounts="s3://my-bucket/data")

        # Verify task was submitted
        assert task.task_id == "task-123"

        # Check that provider.submit_task was called with modified config
        submitted_config = mock_provider.submit_task.call_args[1]['config']
        assert len(submitted_config.data_mounts) == 1
        assert submitted_config.data_mounts[0].source == "s3://my-bucket/data"
        assert submitted_config.data_mounts[0].target == "/data"  # Auto-mounted to /data for S3

    def test_run_with_volume_mount_string(self, flow_client, mock_provider):
        """Test run with volume mount as string."""
        task_config = TaskConfig(
            name="test",
            instance_type="a100",
            command="echo test"
        )

        # Run with single volume mount
        task = flow_client.run(task_config, mounts="volume://my-volume")

        # Check auto-mount path for volumes
        submitted_config = mock_provider.submit_task.call_args[1]['config']
        assert len(submitted_config.data_mounts) == 1
        assert submitted_config.data_mounts[0].source == "volume://my-volume"
        assert submitted_config.data_mounts[0].target == "/mnt"  # Auto-mounted to /mnt for volumes

    def test_run_with_mount_dict(self, flow_client, mock_provider):
        """Test run with mounts as dictionary."""
        task_config = TaskConfig(
            name="test",
            instance_type="a100",
            command="echo test"
        )

        # Run with multiple mounts
        mounts = {
            "/data": "s3://bucket/datasets",
            "/models": "s3://bucket/models",
            "/checkpoints": "volume://checkpoint-vol"
        }
        task = flow_client.run(task_config, mounts=mounts)

        # Verify all mounts were added
        submitted_config = mock_provider.submit_task.call_args[1]['config']
        assert len(submitted_config.data_mounts) == 3

        # Check each mount
        mount_map = {m.target: m for m in submitted_config.data_mounts}
        assert mount_map["/data"].source == "s3://bucket/datasets"
        assert mount_map["/models"].source == "s3://bucket/models"
        assert mount_map["/checkpoints"].source == "volume://checkpoint-vol"

    def test_run_mounts_override_config(self, flow_client, mock_provider):
        """Test that mounts parameter overrides config data_mounts."""
        # Config has existing mounts
        task_config = TaskConfig(
            name="test",
            instance_type="a100",
            command="echo test",
            data_mounts=[
                MountSpec(source="s3://old-bucket/data", target="/old")
            ]
        )

        # Run with new mounts
        task = flow_client.run(task_config, mounts={"new": "s3://new-bucket/data"})

        # Verify old mounts were replaced
        submitted_config = mock_provider.submit_task.call_args[1]['config']
        assert len(submitted_config.data_mounts) == 1
        assert submitted_config.data_mounts[0].source == "s3://new-bucket/data"
        assert submitted_config.data_mounts[0].target == "new"
        # Old mount should be gone
        assert not any(m.target == "/old" for m in submitted_config.data_mounts)

    def test_run_without_mounts(self, flow_client, mock_provider):
        """Test run without mounts parameter."""
        task_config = TaskConfig(
            name="test",
            instance_type="a100",
            command="echo test"
        )

        # Run without mounts
        task = flow_client.run(task_config)

        # Verify no mounts were added
        submitted_config = mock_provider.submit_task.call_args[1]['config']
        assert submitted_config.data_mounts == []

    def test_run_preserves_existing_mounts_without_override(self, flow_client, mock_provider):
        """Test that existing data_mounts are preserved when mounts param not provided."""
        # Config has existing mounts
        existing_mounts = [
            MountSpec(source="s3://bucket/data", target="/data"),
            MountSpec(source="volume://vol-123", target="/models")
        ]
        task_config = TaskConfig(
            name="test",
            instance_type="a100",
            command="echo test",
            data_mounts=existing_mounts
        )

        # Run without mounts parameter
        task = flow_client.run(task_config)

        # Verify existing mounts were preserved
        submitted_config = mock_provider.submit_task.call_args[1]['config']
        assert len(submitted_config.data_mounts) == 2
        assert submitted_config.data_mounts[0].source == "s3://bucket/data"
        assert submitted_config.data_mounts[1].source == "volume://vol-123"


class TestFlowSubmitMounts:
    """Test Flow.submit() with mounts parameter."""

    @pytest.fixture
    def mock_provider(self):
        """Create mock provider with volume operations."""
        provider = Mock()
        provider.prepare_task_config = Mock(side_effect=lambda x: x)
        provider.list_volumes = Mock(return_value=[])
        provider.find_instances = Mock(return_value=[{
            "instance_type": "a100-80gb",
            "price_per_hour": 5.0,
            "gpu_count": 1
        }])
        provider.submit_task = Mock(return_value=Task(
            task_id="task-456",
            name="quick-task",
            status=TaskStatus.PENDING,
            instance_type="a100-80gb",
            region="us-east-1",
            created_at=1234567890,
            num_instances=1,
            cost_per_hour="$5.00"
        ))
        return provider

    @pytest.fixture
    def flow_client(self, mock_provider):
        """Create Flow client with mocked provider."""
        config = Config(
            provider="fcp",
            auth_token="test-token"
        )

        with patch('flow.api.client.create_provider', return_value=mock_provider):
            with patch('flow.api.client.Flow._load_instance_catalog', return_value=[{
                "name": "a100-80gb",
                "instance_type": "a100-80gb.sxm4.1x",
                "gpu_type": "a100-80gb",
                "gpu_count": 1,
                "gpu": {"model": "a100", "memory_gb": 80},
                "price_per_hour": 5.0,
                "available": True
            }]):
                client = Flow(config)
                yield client

    def test_submit_with_single_mount(self, flow_client, mock_provider):
        """Test submit with single mount string."""
        with patch('flow._internal.data.resolver.URLResolver.resolve') as mock_resolve:
            # Mock resolver to return S3 mount spec
            mock_resolve.return_value = MountSpec(
                source="s3://bucket/data",
                target="/data",
                mount_type="s3fs",
                options={"bucket": "bucket", "path": "data"}
            )

            task = flow_client.submit(
                "python train.py",
                gpu="a100",
                mounts="s3://bucket/data"
            )

            assert task.task_id == "task-456"

            # Check environment variables were set for S3 mount
            submitted_config = mock_provider.submit_task.call_args[1]['config']
            assert "S3_MOUNT_0_BUCKET" in submitted_config.env
            assert submitted_config.env["S3_MOUNT_0_BUCKET"] == "bucket"
            assert submitted_config.env["S3_MOUNT_0_PATH"] == "data"
            assert submitted_config.env["S3_MOUNT_0_TARGET"] == "/data"

    def test_submit_with_mount_dict(self, flow_client, mock_provider):
        """Test submit with multiple mounts."""
        with patch('flow._internal.data.resolver.URLResolver.resolve') as mock_resolve:
            # Mock resolver to return different mount types
            def resolve_side_effect(source, target, provider):
                if source.startswith("s3://"):
                    return MountSpec(
                        source=source,
                        target=target,
                        mount_type="s3fs",
                        options={"bucket": "bucket", "path": "path"}
                    )
                else:
                    return MountSpec(
                        source=source,
                        target=target,
                        mount_type="volume",
                        options={"volume_id": "vol-123"}
                    )

            mock_resolve.side_effect = resolve_side_effect

            task = flow_client.submit(
                "python train.py",
                gpu="a100",
                mounts={
                    "/data": "s3://bucket/path",
                    "/models": "volume://model-vol"
                }
            )

            # Check both mount types were handled
            submitted_config = mock_provider.submit_task.call_args[1]['config']

            # S3 mount via env vars
            assert "S3_MOUNT_0_BUCKET" in submitted_config.env

            # Volume mount via volumes list
            assert len(submitted_config.volumes) == 1
            assert submitted_config.volumes[0].volume_id == "vol-123"
            assert submitted_config.volumes[0].mount_path == "/models"
