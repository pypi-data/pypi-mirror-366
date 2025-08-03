"""Tests for FCP provider implementation."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from flow.providers.fcp.core.errors import FCPAPIError
from flow.providers.fcp.provider import FCPProvider
from tests.conftest import create_mock_config


class TestFCPProvider:
    """Test FCP provider API interactions."""

    @pytest.fixture
    def mock_http(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def config(self):
        """Create test config."""
        return create_mock_config(auth_token="test-key", project="test-project", region="us-central1")

    @pytest.fixture
    def provider(self, config, mock_http):
        """Create FCP provider with mocked dependencies."""
        provider = FCPProvider(
            config=config,
            http_client=mock_http
        )
        # Mock project ID resolution
        provider._project_id = "proj_test123"
        return provider

    def test_create_volume_api_payload(self, provider, mock_http):
        """Test that create_volume sends correct API payload."""
        # Mock successful response
        mock_http.request.return_value = {
            "fid": "vol_123",
            "name": "test-volume",
            "region": "us-central1",
            "status": "available",
            "size_gb": 100,
            "created_at": datetime.now().isoformat(),
            "attached_to": []
        }

        # Create volume
        volume = provider.create_volume(size_gb=100, name="test-volume")

        # Verify API was called correctly (second call should be the volume creation)
        assert mock_http.request.call_count >= 1
        volume_call = None
        for call in mock_http.request.call_args_list:
            if call.kwargs.get('url') == '/v2/volumes':
                volume_call = call
                break

        assert volume_call is not None, "No volume creation call found"
        assert volume_call.kwargs['method'] == 'POST'
        assert volume_call.kwargs['json'] == {
            "size_gb": 100,
            "name": "test-volume",
            "project": "proj_test123",  # Should use 'project', not 'project_id'
            "disk_interface": "Block",  # Should include disk_interface
            "region": "us-central1"     # Should include region
        }

        # Verify returned volume
        assert volume.volume_id == "vol_123"
        assert volume.name == "test-volume"
        assert volume.size_gb == 100

    def test_create_volume_uses_default_region(self, mock_http):
        """Test that create_volume uses default region when not configured."""
        # Create provider without region
        config = create_mock_config(auth_token="test-key", project="test-project")
        provider = FCPProvider(config=config, http_client=mock_http)
        provider._project_id = "proj_test123"

        # Mock response
        mock_http.request.return_value = {
            "fid": "vol_123",
            "name": "test-volume",
            "region": "us-central1-a",
            "status": "available",
            "size_gb": 50,
            "created_at": datetime.now().isoformat(),
            "attached_to": []
        }

        # Create volume
        provider.create_volume(size_gb=50, name="test-volume")

        # Verify default region was used
        call_args = mock_http.request.call_args
        assert call_args.kwargs["json"]["region"] == "us-central1-a"

    def test_create_volume_auto_generates_name(self, provider, mock_http):
        """Test that create_volume generates name when not provided."""
        # Mock response
        mock_http.request.return_value = {
            "fid": "vol_123",
            "name": "flow-volume-123456",
            "region": "us-central1",
            "status": "available",
            "size_gb": 200,
            "created_at": datetime.now().isoformat(),
            "attached_to": []
        }

        # Create volume without name
        provider.create_volume(size_gb=200)

        # Verify auto-generated name was sent
        call_args = mock_http.request.call_args
        payload = call_args.kwargs["json"]
        assert payload["name"].startswith("flow-volume-")
        assert len(payload["name"]) > len("flow-volume-")

    def test_create_volume_handles_api_error(self, provider, mock_http):
        """Test that create_volume handles API errors properly."""
        # Mock error response
        mock_http.request.side_effect = Exception("API Error")

        # Should raise FCPAPIError
        with pytest.raises(FCPAPIError) as exc_info:
            provider.create_volume(size_gb=100)

        assert "Create volume failed" in str(exc_info.value)
