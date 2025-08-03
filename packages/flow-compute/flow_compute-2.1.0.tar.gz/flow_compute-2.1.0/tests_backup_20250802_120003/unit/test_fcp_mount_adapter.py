"""Unit tests for FCPMountAdapter."""

import pytest

from flow.api.models import MountSpec
from flow.errors import ValidationError
from flow.providers.fcp.adapters.mounts import FCPMountAdapter


class TestFCPMountAdapter:
    """Test FCP-specific mount adaptation logic."""

    def test_init(self):
        """Test adapter initialization."""
        adapter = FCPMountAdapter()
        assert adapter is not None

    def test_adapt_empty_mounts(self):
        """Test adapting empty mount list."""
        adapter = FCPMountAdapter()
        volumes, env_vars = adapter.adapt_mounts([])

        assert volumes == []
        assert env_vars == {}

    def test_adapt_volume_mount(self):
        """Test adapting volume mount to VolumeSpec."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="volume://vol-123",
                target="/data",
                mount_type="volume",
                options={"volume_id": "vol-123"}
            )
        ]

        volumes, env_vars = adapter.adapt_mounts(mounts)

        assert len(volumes) == 1
        assert volumes[0].volume_id == "vol-123"
        assert volumes[0].mount_path == "/data"
        assert env_vars == {}

    def test_adapt_s3_mount(self):
        """Test adapting S3 mount to environment variables."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="s3://my-bucket/datasets",
                target="/data",
                mount_type="s3fs",
                options={"bucket": "my-bucket", "path": "datasets"}
            )
        ]

        volumes, env_vars = adapter.adapt_mounts(mounts)

        assert volumes == []
        assert env_vars == {
            "S3_MOUNT_0_BUCKET": "my-bucket",
            "S3_MOUNT_0_PATH": "datasets",
            "S3_MOUNT_0_TARGET": "/data",
            "S3_MOUNTS_COUNT": "1"
        }

    def test_adapt_multiple_s3_mounts(self):
        """Test adapting multiple S3 mounts with correct indexing."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="s3://bucket1/data",
                target="/data",
                mount_type="s3fs",
                options={"bucket": "bucket1", "path": "data"}
            ),
            MountSpec(
                source="s3://bucket2/models",
                target="/models",
                mount_type="s3fs",
                options={"bucket": "bucket2", "path": "models"}
            )
        ]

        volumes, env_vars = adapter.adapt_mounts(mounts)

        assert volumes == []
        assert env_vars == {
            "S3_MOUNT_0_BUCKET": "bucket1",
            "S3_MOUNT_0_PATH": "data",
            "S3_MOUNT_0_TARGET": "/data",
            "S3_MOUNT_1_BUCKET": "bucket2",
            "S3_MOUNT_1_PATH": "models",
            "S3_MOUNT_1_TARGET": "/models",
            "S3_MOUNTS_COUNT": "2"
        }

    def test_adapt_mixed_mounts(self):
        """Test adapting mix of volume and S3 mounts."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="volume://vol-abc",
                target="/checkpoints",
                mount_type="volume",
                options={"volume_id": "vol-abc"}
            ),
            MountSpec(
                source="s3://datasets/imagenet",
                target="/data",
                mount_type="s3fs",
                options={"bucket": "datasets", "path": "imagenet"}
            )
        ]

        volumes, env_vars = adapter.adapt_mounts(mounts)

        assert len(volumes) == 1
        assert volumes[0].volume_id == "vol-abc"
        assert volumes[0].mount_path == "/checkpoints"

        assert env_vars == {
            "S3_MOUNT_0_BUCKET": "datasets",
            "S3_MOUNT_0_PATH": "imagenet",
            "S3_MOUNT_0_TARGET": "/data",
            "S3_MOUNTS_COUNT": "1"
        }

    def test_adapt_unsupported_mount_type(self):
        """Test error on unsupported mount type."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="/local/path",
                target="/share",
                mount_type="bind",
                options={}
            )
        ]

        with pytest.raises(ValidationError) as exc_info:
            adapter.adapt_mounts(mounts)

        assert "FCP does not support mount type: bind" in str(exc_info.value)
        assert "Only volume:// and s3:// are supported" in str(exc_info.value)

    def test_volume_mount_missing_volume_id(self):
        """Test error when volume mount missing volume_id."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="volume://missing",
                target="/data",
                mount_type="volume",
                options={}  # Missing volume_id
            )
        ]

        with pytest.raises(ValidationError) as exc_info:
            adapter.adapt_mounts(mounts)

        assert "Volume mount missing volume_id" in str(exc_info.value)

    def test_s3_mount_missing_bucket(self):
        """Test error when S3 mount missing bucket."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="s3://invalid",
                target="/data",
                mount_type="s3fs",
                options={"path": "data"}  # Missing bucket
            )
        ]

        with pytest.raises(ValidationError) as exc_info:
            adapter.adapt_mounts(mounts)

        assert "S3 mount missing bucket" in str(exc_info.value)

    def test_s3_mount_empty_path(self):
        """Test S3 mount with empty path (mount bucket root)."""
        adapter = FCPMountAdapter()
        mounts = [
            MountSpec(
                source="s3://my-bucket",
                target="/data",
                mount_type="s3fs",
                options={"bucket": "my-bucket"}  # No path = root
            )
        ]

        volumes, env_vars = adapter.adapt_mounts(mounts)

        assert env_vars["S3_MOUNT_0_PATH"] == ""
        assert env_vars["S3_MOUNT_0_BUCKET"] == "my-bucket"
