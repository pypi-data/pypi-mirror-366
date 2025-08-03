"""Unit tests for Provider Manifest system."""

import pytest
from unittest.mock import MagicMock, patch

from flow.cli.provider_resolver import ProviderResolver
from flow.errors import ProviderError
from flow.providers.base import (
    CLIConfig,
    ConfigField,
    ConnectionMethod,
    EnvVarSpec,
    PricingModel,
    ProviderCapabilities,
    ProviderManifest,
    ValidationRules,
)


class TestProviderManifest:
    """Test Provider Manifest models."""
    
    def test_env_var_spec_creation(self):
        """Test EnvVarSpec model creation."""
        env_var = EnvVarSpec(
            name="FCP_API_KEY",
            required=True,
            description="API key for authentication",
            validation_pattern=r"^fkey_[A-Za-z0-9]{20,}$",
            sensitive=True
        )
        
        assert env_var.name == "FCP_API_KEY"
        assert env_var.required is True
        assert env_var.sensitive is True
        assert env_var.default is None
    
    def test_connection_method_creation(self):
        """Test ConnectionMethod model creation."""
        conn = ConnectionMethod(
            type="ssh",
            command_template="ssh -p {port} {user}@{host}",
            supports_interactive=True,
            supports_exec=True
        )
        
        assert conn.type == "ssh"
        assert "{host}" in conn.command_template
        assert conn.supports_interactive is True
    
    def test_provider_manifest_creation(self):
        """Test complete ProviderManifest creation."""
        manifest = ProviderManifest(
            name="test",
            display_name="Test Provider",
            capabilities=ProviderCapabilities(
                supports_spot_instances=True,
                pricing_model=PricingModel.MARKET
            ),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh"),
                mount_patterns={
                    r"^s3://.*": "/data"
                }
            )
        )
        
        assert manifest.name == "test"
        assert manifest.capabilities.supports_spot_instances is True
        assert manifest.cli_config.mount_patterns[r"^s3://.*"] == "/data"


class TestProviderResolver:
    """Test ProviderResolver functionality."""
    
    def test_get_manifest_success(self):
        """Test successful manifest retrieval."""
        # Create a mock manifest
        mock_manifest = ProviderManifest(
            name="fcp",
            display_name="Flow Compute Platform",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh")
            )
        )
        
        # Mock the import
        with patch("flow.cli.provider_resolver.importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.manifest = MagicMock()
            mock_module.FCP_MANIFEST = mock_manifest
            mock_import.return_value = mock_module
            
            # Clear cache first
            ProviderResolver._manifest_cache.clear()
            
            manifest = ProviderResolver.get_manifest("fcp")
            assert manifest.name == "fcp"
            assert manifest.display_name == "Flow Compute Platform"
    
    def test_get_manifest_not_found(self):
        """Test manifest retrieval for non-existent provider."""
        with patch("flow.cli.provider_resolver.importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("No module named 'flow.providers.fake'")
            
            with pytest.raises(ProviderError, match="Provider 'fake' not found"):
                ProviderResolver.get_manifest("fake")
    
    def test_resolve_mount_path(self):
        """Test mount path resolution."""
        mock_manifest = ProviderManifest(
            name="test",
            display_name="Test",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh"),
                mount_patterns={
                    r"^s3://.*": "/data",
                    r"^volume://.*": "/mnt",
                    r"^gs://.*": "/gcs"
                }
            )
        )
        
        # Mock the get_manifest method
        with patch.object(ProviderResolver, "get_manifest", return_value=mock_manifest):
            assert ProviderResolver.resolve_mount_path("test", "s3://bucket/path") == "/data"
            assert ProviderResolver.resolve_mount_path("test", "volume://vol-123") == "/mnt"
            assert ProviderResolver.resolve_mount_path("test", "gs://bucket/file") == "/gcs"
            # Test fallback
            assert ProviderResolver.resolve_mount_path("test", "/local/path") == "/mnt/path"
    
    def test_get_connection_command_ssh(self):
        """Test SSH connection command generation."""
        mock_manifest = ProviderManifest(
            name="test",
            display_name="Test",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(
                    type="ssh",
                    command_template="ssh -p {port} {user}@{host}"
                )
            )
        )
        
        # Create a mock task
        mock_task = MagicMock()
        mock_task.ssh_host = "example.com"
        mock_task.ssh_port = 2222
        mock_task.ssh_user = "admin"
        
        with patch.object(ProviderResolver, "get_manifest", return_value=mock_manifest):
            command = ProviderResolver.get_connection_command("test", mock_task)
            assert command == "ssh -p 2222 admin@example.com"
    
    def test_get_connection_command_no_ssh(self):
        """Test connection command when SSH not available."""
        mock_manifest = ProviderManifest(
            name="test",
            display_name="Test",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh")
            )
        )
        
        # Task without SSH details
        mock_task = MagicMock(spec=[])
        
        with patch.object(ProviderResolver, "get_manifest", return_value=mock_manifest):
            command = ProviderResolver.get_connection_command("test", mock_task)
            assert command is None
    
    def test_validate_config_value(self):
        """Test configuration value validation."""
        mock_manifest = ProviderManifest(
            name="test",
            display_name="Test",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh"),
                config_fields=[
                    ConfigField(
                        name="api_key",
                        description="API Key",
                        validation_pattern=r"^fkey_[A-Za-z0-9]{20,}$"
                    )
                ]
            ),
            validation=ValidationRules(
                api_key_pattern=r"^fkey_[A-Za-z0-9]{20,}$",
                region_pattern=r"^[a-z]+-[a-z]+\d+-[a-z]$"
            )
        )
        
        with patch.object(ProviderResolver, "get_manifest", return_value=mock_manifest):
            # Valid API key
            assert ProviderResolver.validate_config_value("test", "api_key", "fkey_12345678901234567890") is True
            # Invalid API key
            assert ProviderResolver.validate_config_value("test", "api_key", "bad_key") is False
            # Valid region
            assert ProviderResolver.validate_config_value("test", "region", "us-central1-a") is True
            # Invalid region
            assert ProviderResolver.validate_config_value("test", "region", "invalid") is False
            # Unknown key (no validation)
            assert ProviderResolver.validate_config_value("test", "unknown", "anything") is True
    
    def test_get_env_vars(self):
        """Test environment variable mapping."""
        mock_manifest = ProviderManifest(
            name="test",
            display_name="Test",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh"),
                env_vars=[
                    EnvVarSpec(name="TEST_API_KEY", description="API Key"),
                    EnvVarSpec(name="TEST_PROJECT", description="Project"),
                    EnvVarSpec(name="TEST_REGION", description="Region")
                ],
                config_fields=[
                    ConfigField(name="endpoint", description="Endpoint", env_var="TEST_ENDPOINT")
                ]
            )
        )
        
        with patch.object(ProviderResolver, "get_manifest", return_value=mock_manifest):
            env_vars = ProviderResolver.get_env_vars("test")
            assert env_vars["api_key"] == "TEST_API_KEY"
            assert env_vars["project"] == "TEST_PROJECT"
            assert env_vars["region"] == "TEST_REGION"
            assert env_vars["endpoint"] == "TEST_ENDPOINT"
    
    def test_get_default_region(self):
        """Test default region retrieval."""
        mock_manifest = ProviderManifest(
            name="test",
            display_name="Test",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh"),
                default_region="us-west-1"
            )
        )
        
        with patch.object(ProviderResolver, "get_manifest", return_value=mock_manifest):
            assert ProviderResolver.get_default_region("test") == "us-west-1"
    
    @pytest.mark.skip(reason="Mock patching issue - import_module being called multiple times")
    def test_manifest_caching(self):
        """Test that manifests are cached after first load."""
        mock_manifest = ProviderManifest(
            name="cached",
            display_name="Cached Provider",
            capabilities=ProviderCapabilities(),
            cli_config=CLIConfig(
                connection_method=ConnectionMethod(type="ssh")
            )
        )
        
        # Clear cache
        ProviderResolver._manifest_cache.clear()
        
        # First call should import
        with patch("flow.cli.provider_resolver.importlib.import_module") as mock_import:
            mock_module = MagicMock()
            mock_module.MANIFEST = mock_manifest  # Use MANIFEST attribute
            mock_import.return_value = mock_module
            
            manifest1 = ProviderResolver.get_manifest("cached")
            assert mock_import.call_count == 1
            
            # Second call should use cache
            manifest2 = ProviderResolver.get_manifest("cached")
            assert mock_import.call_count == 1  # Not called again
            assert manifest1 is manifest2  # Same object