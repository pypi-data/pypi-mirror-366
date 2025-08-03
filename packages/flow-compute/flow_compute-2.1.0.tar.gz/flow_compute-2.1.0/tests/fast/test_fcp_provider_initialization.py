"""Unit tests for FCP provider initialization and configuration.

These tests focus on provider setup, configuration validation,
and initialization logic.
"""

from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.providers.fcp.provider import FCPProvider


@pytest.mark.unit
@pytest.mark.quick


class TestFCPProviderInitialization:
    """Test FCP provider initialization and configuration."""

    def test_provider_init_with_config(self):
        """Test provider initialization with configuration."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )
        
        provider = FCPProvider(config)
        
        assert provider.config == config
        assert provider.api_url == "https://api.test.com"
        # Project ID is resolved lazily
        assert provider._project_id is None

    def test_provider_init_with_custom_http_client(self):
        """Test provider accepts custom HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )
        mock_http = Mock()
        
        provider = FCPProvider(config, http_client=mock_http)
        
        assert provider.http == mock_http

    def test_provider_init_defaults(self):
        """Test provider initialization with minimal config."""
        config = Config(
            provider="fcp",
            auth_token="test-token"
        )
        
        provider = FCPProvider(config)
        
        # Should use default API URL
        assert provider.api_url == "https://api.foundationcloudplatform.com"

    def test_provider_lazy_project_resolution(self):
        """Test that project ID is resolved lazily on first use."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "my-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        
        # Initially None
        assert provider._project_id is None
        
        # Mock the project resolver response
        mock_http.request = Mock(return_value=[{
            "fid": "proj-123",
            "name": "my-project"
        }])
        
        # Access project_id property triggers resolution
        project_id = provider.project_id
        
        assert project_id == "proj-123"
        assert provider._project_id == "proj-123"
        
        # Should cache and not call API again
        mock_http.request.reset_mock()
        project_id2 = provider.project_id
        assert project_id2 == "proj-123"
        mock_http.request.assert_not_called()

    def test_provider_project_resolution_error(self):
        """Test error handling during project resolution."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "nonexistent-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        
        # Mock empty response (project not found)
        mock_http.request = Mock(return_value=[])
        
        with pytest.raises(ValueError) as exc_info:
            _ = provider.project_id
        
        assert "Project 'nonexistent-project' not found" in str(exc_info.value)