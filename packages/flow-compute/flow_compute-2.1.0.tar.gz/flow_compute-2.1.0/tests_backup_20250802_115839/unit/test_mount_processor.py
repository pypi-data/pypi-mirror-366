"""Unit tests for MountProcessor class."""

from unittest.mock import Mock

import pytest

from flow._internal.data.mount_processor import MountProcessor
from flow.api.models import MountSpec, TaskConfig
from flow.errors import ValidationError


class TestMountProcessor:
    """Test MountProcessor data mounting logic."""

    def test_init(self):
        """Test MountProcessor initialization."""
        processor = MountProcessor()
        assert processor._resolver is not None

    def test_process_mounts_empty(self):
        """Test processing with no mounts."""
        processor = MountProcessor()
        config = TaskConfig(
            name="test",
            image="test",
            command="echo test",
            instance_type="a100"
        )
        provider = Mock()

        result = processor.process_mounts(config, provider)
        assert result == []

    def test_process_mounts_valid(self):
        """Test processing valid mounts."""
        processor = MountProcessor()
        config = TaskConfig(
            name="test",
            image="test",
            command="echo test",
            instance_type="a100",
            data_mounts=[
                MountSpec(source="s3://bucket/data", target="/data"),
                MountSpec(source="volume://vol-123", target="/models")
            ]
        )
        provider = Mock()

        # Mock resolver to return resolved mounts
        processor._resolver.resolve = Mock(side_effect=lambda source, target, prov:
            MountSpec(
                source=source,
                target=target,
                mount_type="s3fs" if source.startswith("s3://") else "volume",
                options={"bucket": "bucket", "path": "data"} if source.startswith("s3://")
                    else {"volume_id": "vol-123"}
            )
        )

        result = processor.process_mounts(config, provider)

        assert len(result) == 2
        assert result[0].mount_type == "s3fs"
        assert result[0].target == "/data"
        assert result[1].mount_type == "volume"
        assert result[1].target == "/models"

    def test_process_mounts_dict_format(self):
        """Test processing mounts in dict format."""
        processor = MountProcessor()
        config = TaskConfig(
            name="test",
            image="test",
            command="echo test",
            instance_type="a100",
            data_mounts=[
                {"source": "s3://bucket/data", "target": "/data"}
            ]
        )
        provider = Mock()

        # Mock resolver
        processor._resolver.resolve = Mock(return_value=MountSpec(
            source="s3://bucket/data",
            target="/data",
            mount_type="s3fs",
            options={"bucket": "bucket", "path": "data"}
        ))

        result = processor.process_mounts(config, provider)

        assert len(result) == 1
        assert result[0].mount_type == "s3fs"

    def test_process_mounts_resolution_error(self):
        """Test error handling during mount resolution."""
        processor = MountProcessor()
        config = TaskConfig(
            name="test",
            image="test",
            command="echo test",
            instance_type="a100",
            data_mounts=[
                MountSpec(source="s3://valid-bucket/data", target="/data")
            ]
        )
        provider = Mock()

        # Mock resolver to raise error
        processor._resolver.resolve = Mock(side_effect=Exception("Unknown protocol"))

        with pytest.raises(ValidationError) as exc_info:
            processor.process_mounts(config, provider)

        assert "Failed to resolve mount s3://valid-bucket/data" in str(exc_info.value)

    def test_validate_mounts_duplicate_targets(self):
        """Test validation catches duplicate mount targets."""
        processor = MountProcessor()
        mounts = [
            MountSpec(source="s3://bucket1/data", target="/data"),
            MountSpec(source="s3://bucket2/data", target="/data")
        ]

        with pytest.raises(ValidationError) as exc_info:
            processor._validate_mounts(mounts)

        assert "Duplicate mount target: /data" in str(exc_info.value)

    def test_validate_mounts_relative_path(self):
        """Test validation catches relative mount paths."""
        processor = MountProcessor()
        mounts = [
            MountSpec(source="s3://bucket/data", target="data")
        ]

        with pytest.raises(ValidationError) as exc_info:
            processor._validate_mounts(mounts)

        assert "Mount target must be absolute path: data" in str(exc_info.value)

    def test_validate_mounts_invalid_source(self):
        """Test validation catches invalid source format."""
        processor = MountProcessor()
        mounts = [
            MountSpec(source="http://example.com/data", target="/data")
        ]

        with pytest.raises(ValidationError) as exc_info:
            processor._validate_mounts(mounts)

        assert "Invalid mount source: http://example.com/data" in str(exc_info.value)
        assert "Must start with s3://, volume://, or /" in str(exc_info.value)

    def test_validate_mounts_system_directory(self):
        """Test validation prevents mounting over system directories."""
        processor = MountProcessor()

        # Test exact match
        mounts = [MountSpec(source="s3://bucket/data", target="/etc")]
        with pytest.raises(ValidationError) as exc_info:
            processor._validate_mounts(mounts)
        assert "Cannot mount over system directory: /etc" in str(exc_info.value)

        # Test subdirectory
        mounts = [MountSpec(source="s3://bucket/data", target="/usr/local")]
        with pytest.raises(ValidationError) as exc_info:
            processor._validate_mounts(mounts)
        assert "Cannot mount over system directory: /usr/local" in str(exc_info.value)

    def test_validate_mounts_mixed_formats(self):
        """Test validation with mixed dict and MountSpec formats."""
        processor = MountProcessor()
        mounts = [
            {"source": "s3://bucket/data", "target": "/data"},
            MountSpec(source="volume://vol-123", target="/models")
        ]

        # Should validate without errors
        processor._validate_mounts(mounts)

    def test_performance_warning(self, caplog):
        """Test performance warning for slow resolution."""
        import time
        processor = MountProcessor()
        config = TaskConfig(
            name="test",
            image="test",
            command="echo test",
            instance_type="a100",
            data_mounts=[
                MountSpec(source="s3://bucket/data", target="/data")
            ]
        )
        provider = Mock()

        # Mock slow resolver
        def slow_resolve(source, target, prov):
            time.sleep(0.2)  # Simulate slow resolution
            return MountSpec(
                source=source,
                target=target,
                mount_type="s3fs",
                options={"bucket": "bucket", "path": "data"}
            )

        processor._resolver.resolve = Mock(side_effect=slow_resolve)

        result = processor.process_mounts(config, provider)

        # Check warning was logged
        assert any("Mount resolution took" in record.message for record in caplog.records)
