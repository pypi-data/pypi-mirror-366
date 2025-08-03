"""Test URL resolution."""

import os
import tempfile
from unittest.mock import Mock

import pytest

from flow._internal.data.loaders import VolumeLoader
from flow._internal.data.resolver import DataError, URLResolver
from flow.api.models import MountSpec


class TestURLResolver:
    """Test URL resolution to mount specifications."""

    def setup_method(self):
        self.resolver = URLResolver()
        self.mock_provider = Mock()

    def test_local_path_resolution(self):
        """Test local file path resolution."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Test absolute path
            spec = self.resolver.resolve(tmp_path, "/data", self.mock_provider)
            assert spec.source == tmp_path
            assert spec.target == "/data"
            assert spec.mount_type == "bind"
            assert spec.options == {"readonly": True}

            # Test relative path (should be converted to absolute)
            rel_path = os.path.basename(tmp_path)
            os.chdir(os.path.dirname(tmp_path))
            spec = self.resolver.resolve(rel_path, "/data", self.mock_provider)
            # Use realpath to handle macOS symlinks
            assert os.path.realpath(spec.source) == os.path.realpath(tmp_path)
        finally:
            os.unlink(tmp_path)

    def test_file_url_resolution(self):
        """Test file:// URL resolution."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            file_url = f"file://{tmp_path}"
            spec = self.resolver.resolve(file_url, "/data", self.mock_provider)
            assert spec.source == tmp_path
            assert spec.mount_type == "bind"
        finally:
            os.unlink(tmp_path)

    def test_nonexistent_path_error(self):
        """Test error for nonexistent local path."""
        with pytest.raises(DataError) as exc:
            self.resolver.resolve("/nonexistent/path", "/data", self.mock_provider)

        assert "Local path does not exist" in str(exc.value)
        assert "Check the path exists" in str(exc.value)

    def test_unsupported_scheme_error(self):
        """Test error for unsupported URL scheme."""
        with pytest.raises(DataError) as exc:
            self.resolver.resolve("ftp://server/data", "/data", self.mock_provider)

        assert "Unsupported URL scheme: ftp" in str(exc.value)

    def test_volume_url_resolution(self):
        """Test volume:// URL resolution."""
        # Add volume loader
        self.resolver.add_loader("volume", VolumeLoader())

        # Mock provider to return volume
        self.mock_provider.is_volume_id.return_value = False  # "my-data" is not an ID
        self.mock_provider.list_volumes.return_value = [
            {"name": "my-data", "id": "vol_123"}
        ]

        spec = self.resolver.resolve("volume://my-data", "/data", self.mock_provider)
        assert spec.source == "volume://vol_123"
        assert spec.target == "/data"
        assert spec.mount_type == "volume"
        assert spec.options == {"volume_id": "vol_123"}

    def test_target_override(self):
        """Test that resolver overrides target from loader."""
        # Add a mock loader
        mock_loader = Mock()
        mock_loader.resolve.return_value = MountSpec(
            source="test://source",
            target="/wrong/target",
            mount_type="bind"
        )

        self.resolver.add_loader("test", mock_loader)

        spec = self.resolver.resolve("test://data", "/correct/target", self.mock_provider)
        assert spec.target == "/correct/target"  # Should override


class TestVolumeLoader:
    """Test volume URL loading."""

    def setup_method(self):
        self.loader = VolumeLoader()
        self.mock_provider = Mock()
        # Mock is_volume_id to recognize volume IDs
        self.mock_provider.is_volume_id.side_effect = lambda x: x.startswith("vol_")

    def test_volume_id_direct(self):
        """Test direct volume ID usage."""
        spec = self.loader.resolve("volume://vol_abc123", self.mock_provider)
        assert spec.source == "volume://vol_abc123"
        assert spec.mount_type == "volume"
        assert spec.options == {"volume_id": "vol_abc123"}

        # Provider should check if it's an ID but not list volumes
        self.mock_provider.is_volume_id.assert_called_with("vol_abc123")
        self.mock_provider.list_volumes.assert_not_called()

    def test_volume_name_resolution(self):
        """Test volume name to ID resolution."""
        # Mock provider to return volume
        self.mock_provider.list_volumes.return_value = [
            {"name": "training-data", "id": "vol_xyz789"}
        ]

        spec = self.loader.resolve("volume://training-data", self.mock_provider)
        assert spec.source == "volume://vol_xyz789"
        assert spec.options == {"volume_id": "vol_xyz789"}

        # Should have queried provider
        self.mock_provider.list_volumes.assert_called_once_with(limit=1000)

    def test_volume_name_caching(self):
        """Test that volume names are cached."""
        self.mock_provider.list_volumes.return_value = [
            {"name": "cached-data", "id": "vol_cached"}
        ]

        # First call
        spec1 = self.loader.resolve("volume://cached-data", self.mock_provider)
        assert spec1.options["volume_id"] == "vol_cached"

        # Second call should use cache
        spec2 = self.loader.resolve("volume://cached-data", self.mock_provider)
        assert spec2.options["volume_id"] == "vol_cached"

        # Provider should only be called once
        assert self.mock_provider.list_volumes.call_count == 1

    def test_volume_creation_on_missing(self):
        """Test automatic volume creation when name not found."""
        # Mock empty volume list
        self.mock_provider.list_volumes.return_value = []

        # Mock volume creation
        mock_volume = Mock()
        mock_volume.volume_id = "vol_new123"
        self.mock_provider.create_volume.return_value = mock_volume

        spec = self.loader.resolve("volume://new-volume", self.mock_provider)
        assert spec.options["volume_id"] == "vol_new123"

        # Should have created volume
        self.mock_provider.create_volume.assert_called_once_with(
            size_gb=100,
            name="new-volume"
        )

    def test_invalid_volume_url(self):
        """Test error on invalid volume URL."""
        with pytest.raises(DataError) as exc:
            self.loader.resolve("volume://", self.mock_provider)

        assert "Invalid volume URL" in str(exc.value)
        assert "Use volume://name or volume://vol_id" in str(exc.value)

    def test_handle_volume_objects(self):
        """Test handling of Volume objects vs dicts."""
        # Test with Volume objects
        mock_volume = Mock()
        mock_volume.name = "object-volume"
        mock_volume.volume_id = "vol_obj123"

        self.mock_provider.list_volumes.return_value = [mock_volume]

        spec = self.loader.resolve("volume://object-volume", self.mock_provider)
        assert spec.options["volume_id"] == "vol_obj123"
