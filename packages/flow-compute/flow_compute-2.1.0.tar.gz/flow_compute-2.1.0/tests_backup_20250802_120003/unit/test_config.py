"""Tests for Flow SDK configuration."""
import os
from unittest.mock import patch

import pytest

from flow._internal.config import Config, FCPConfig, get_provider_config_class


class TestConfig:
    """Test provider-agnostic Config class."""

    def test_config_creation(self):
        """Test creating config with all parameters."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={"project": "test-project", "region": "us-central1-a"}
        )
        assert config.provider == "fcp"
        assert config.auth_token == "test-token"
        assert config.provider_config["project"] == "test-project"
        assert config.provider_config["region"] == "us-central1-a"

    def test_config_defaults(self):
        """Test config with defaults."""
        config = Config(auth_token="test-token")
        assert config.provider == "fcp"  # default
        assert config.auth_token == "test-token"
        assert config.provider_config == {}

    def test_from_env_all_values(self, monkeypatch):
        """Test loading config from environment with all values."""
        monkeypatch.setenv("FLOW_PROVIDER", "fcp")
        monkeypatch.setenv("FCP_API_KEY", "env-token")
        monkeypatch.setenv("FCP_API_URL", "https://env.api.com")
        monkeypatch.setenv("FCP_DEFAULT_PROJECT", "env-project")
        monkeypatch.setenv("FCP_DEFAULT_REGION", "eu-central1-a")
        monkeypatch.setenv("FCP_SSH_KEYS", "key-1,key-2,key-3")

        config = Config.from_env()
        assert config.provider == "fcp"
        assert config.auth_token == "env-token"
        assert config.provider_config["api_url"] == "https://env.api.com"
        assert config.provider_config["project"] == "env-project"
        assert config.provider_config["region"] == "eu-central1-a"
        assert config.provider_config["ssh_keys"] == ["key-1", "key-2", "key-3"]

    def test_from_env_minimal(self, monkeypatch):
        """Test loading config from environment with minimal values."""
        monkeypatch.setenv("FCP_API_KEY", "minimal-token")
        # Clear other env vars
        for key in ["FLOW_PROVIDER", "FCP_API_URL", "FCP_DEFAULT_PROJECT",
                    "FCP_DEFAULT_REGION", "FCP_SSH_KEYS"]:
            monkeypatch.delenv(key, raising=False)

        # Mock config file loading to prevent picking up global config
        from unittest.mock import patch
        with patch('flow._internal.config_loader.ConfigLoader._load_config_file', return_value={}):
            config = Config.from_env()
            assert config.provider == "fcp"  # default
            assert config.auth_token == "minimal-token"
            assert config.provider_config["api_url"] == "https://api.mlfoundry.com"  # default
            assert "project" not in config.provider_config
            assert "region" not in config.provider_config
            assert "ssh_keys" not in config.provider_config

    def test_from_env_missing_auth_token(self, monkeypatch):
        """Test that missing auth token raises error."""
        monkeypatch.delenv("FCP_API_KEY", raising=False)

        # Mock ConfigLoader to return no API key
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None
            # Should raise error when auth is required but not configured
            with pytest.raises(ValueError, match="Authentication not configured"):
                Config.from_env(require_auth=True)

    def test_from_env_empty_ssh_keys(self, monkeypatch):
        """Test empty SSH keys string."""
        monkeypatch.setenv("FCP_API_KEY", "test-token")
        monkeypatch.setenv("FCP_SSH_KEYS", "")

        config = Config.from_env()
        assert "ssh_keys" not in config.provider_config

    def test_from_env_ssh_keys_with_spaces(self, monkeypatch):
        """Test SSH keys parsing with spaces."""
        monkeypatch.setenv("FCP_API_KEY", "test-token")
        monkeypatch.setenv("FCP_SSH_KEYS", " key-1 , key-2 , key-3 ")

        config = Config.from_env()
        assert config.provider_config["ssh_keys"] == ["key-1", "key-2", "key-3"]

    def test_get_headers(self):
        """Test getting HTTP headers."""
        config = Config(auth_token="test-token-123")
        headers = config.get_headers()

        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["Content-Type"] == "application/json"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_clean_environment(self):
        """Test from_env with clean environment."""
        # Mock ConfigLoader to return no API key
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None
            # Should raise error when auth is required but not configured
            with pytest.raises(ValueError, match="Authentication not configured"):
                Config.from_env(require_auth=True)


class TestFCPConfig:
    """Test FCP-specific configuration class."""

    def test_fcp_config_creation(self):
        """Test creating FCP config."""
        config = FCPConfig(
            api_url="https://test.api.com",
            project="test-project",
            region="us-central1-a",
            ssh_keys=["key-1", "key-2"]
        )
        assert config.api_url == "https://test.api.com"
        assert config.project == "test-project"
        assert config.region == "us-central1-a"
        assert config.ssh_keys == ["key-1", "key-2"]

    def test_fcp_config_defaults(self):
        """Test FCP config with defaults."""
        config = FCPConfig()
        assert config.api_url == "https://api.mlfoundry.com"
        assert config.project is None
        assert config.region is None
        assert config.ssh_keys is None

    def test_fcp_config_from_dict(self):
        """Test creating FCP config from dictionary."""
        data = {
            "api_url": "https://dict.api.com",
            "project": "dict-project",
            "region": "eu-central1-a",
            "ssh_keys": ["key-a", "key-b"]
        }
        config = FCPConfig.from_dict(data)
        assert config.api_url == "https://dict.api.com"
        assert config.project == "dict-project"
        assert config.region == "eu-central1-a"
        assert config.ssh_keys == ["key-a", "key-b"]

    def test_fcp_config_from_dict_partial(self):
        """Test creating FCP config from partial dictionary."""
        data = {"project": "partial-project"}
        config = FCPConfig.from_dict(data)
        assert config.api_url == "https://api.mlfoundry.com"  # default
        assert config.project == "partial-project"
        assert config.region is None
        assert config.ssh_keys is None


class TestProviderRegistry:
    """Test provider configuration registry."""

    def test_get_provider_config_class_fcp(self):
        """Test getting FCP config class."""
        cls = get_provider_config_class("fcp")
        assert cls is FCPConfig

    def test_get_provider_config_class_unknown(self):
        """Test getting unknown provider config class."""
        with pytest.raises(ValueError, match="Unknown provider: aws"):
            get_provider_config_class("aws")
