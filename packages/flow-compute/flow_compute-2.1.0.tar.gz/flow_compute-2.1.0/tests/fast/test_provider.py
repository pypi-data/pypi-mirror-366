"""Unit tests for provider architecture.

These tests focus on our provider logic, not mocking entire providers.
We test factory behavior, configuration handling, and error cases.
"""

from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.providers.factory import create_provider
from flow.providers.fcp.provider import FCPProvider
from flow.providers.registry import ProviderNotFoundError


class TestProviderFactory:
    """Test provider factory behavior."""

    def test_create_fcp_provider_from_config(self):
        """Test creating FCP provider with proper configuration."""
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={
                "api_url": "https://api.mlfoundry.com",
                "project": "test-project"
            }
        )

        provider = create_provider(config)

        # Verify correct type
        assert isinstance(provider, FCPProvider)
        # Verify configuration was passed through
        assert provider.config == config
        assert provider.auth_token == "test-key"

    def test_create_provider_with_missing_auth(self):
        """Test provider creation with missing auth token."""
        # Provider creation doesn't validate auth token - that happens during use
        config = Config(
            provider="fcp",
            auth_token=None,
            provider_config={}
        )

        # Should create but may fail on first API call
        provider = create_provider(config)
        assert provider is not None

    def test_unknown_provider_raises_error(self):
        """Test that unknown provider names raise appropriate error."""
        config = Config(
            provider="unknown-provider",
            auth_token="test-key",
            provider_config={}
        )

        with pytest.raises(ProviderNotFoundError, match="unknown-provider"):
            create_provider(config)

    def test_provider_name_lowercase_only(self):
        """Test that provider names must be lowercase."""
        # Valid lowercase
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"api_url": "https://api.mlfoundry.com"}
        )

        provider = create_provider(config)
        assert isinstance(provider, FCPProvider)

        # Invalid uppercase should fail
        config_upper = Config(
            provider="FCP",
            auth_token="test-key",
            provider_config={"api_url": "https://api.mlfoundry.com"}
        )

        with pytest.raises(ProviderNotFoundError):
            create_provider(config_upper)


class TestProviderConfiguration:
    """Test provider configuration handling."""

    def test_fcp_provider_requires_fcp_config(self):
        """Test that FCP provider validates its configuration type."""
        config = Config(
            provider="other",  # Wrong provider type
            auth_token="test-key",
            provider_config={}
        )

        mock_http = Mock()

        with pytest.raises(ValueError, match="requires 'fcp' provider"):
            FCPProvider(config, http_client=mock_http)

    def test_fcp_provider_extracts_config(self):
        """Test FCP provider extracts its specific configuration."""
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "my-project",
                "region": "us-east-1"
            }
        )

        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)

        # Verify FCP-specific config extracted
        assert provider.fcp_config.api_url == "https://api.test.com"
        assert provider.fcp_config.project == "my-project"
        assert provider.fcp_config.region == "us-east-1"

    def test_provider_initialization_error_handling(self):
        """Test provider handles initialization errors gracefully."""
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={"project": "test-project"}
        )

        # Mock HTTP client that fails during project resolution
        mock_http = Mock()
        mock_http.get.side_effect = Exception("Network error")

        # Should not crash during init, just log warning
        provider = FCPProvider(config, http_client=mock_http)

        # Provider should still be usable
        assert provider is not None
        assert provider._project_id is None  # Failed to resolve


class TestProviderRegistry:
    """Test provider registration system."""

    def test_registry_has_fcp_provider(self):
        """Test that FCP provider is registered."""
        from flow.providers.registry import ProviderRegistry

        # Should be able to get FCP provider class
        fcp_class = ProviderRegistry.get("fcp")
        assert fcp_class is not None
        assert fcp_class.__name__ == "FCPProvider"

    def test_registry_auto_discovery(self):
        """Test that registry auto-discovers providers."""
        from flow.providers.registry import ProviderRegistry

        # Force initialization
        ProviderRegistry._auto_discover()

        # FCP should be discovered
        assert "fcp" in ProviderRegistry._providers


class TestProviderInterfaceCompliance:
    """Test that providers implement required interfaces correctly."""

    def test_fcp_provider_implements_compute_interface(self):
        """Test FCP provider implements IComputeProvider interface."""
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={}
        )

        provider = create_provider(config)

        # Verify interface methods exist (actual method names)
        assert hasattr(provider, "find_instances")
        assert hasattr(provider, "submit_task")
        assert hasattr(provider, "get_task")
        assert hasattr(provider, "get_task_status")
        assert hasattr(provider, "cancel_task")
        assert hasattr(provider, "list_tasks")
        assert hasattr(provider, "get_task_logs")  # Not get_logs

    def test_fcp_provider_implements_storage_interface(self):
        """Test FCP provider implements IStorageProvider interface."""
        config = Config(
            provider="fcp",
            auth_token="test-key",
            provider_config={}
        )

        provider = create_provider(config)

        # Verify storage interface methods exist
        assert hasattr(provider, "create_volume")
        assert hasattr(provider, "delete_volume")
        assert hasattr(provider, "list_volumes")
        # Note: FCP manages volume attachment through task submission
        # not separate attach/detach methods
