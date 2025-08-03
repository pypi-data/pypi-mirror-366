"""Integration tests for CLI commands using Provider Manifest system."""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from flow.cli.commands.init import InitCommand
from flow.cli.commands.run import RunCommand
from flow.cli.commands.ssh import SSHCommand
from flow.cli.provider_resolver import ProviderResolver
from flow.cli.utils.config_validator import ConfigValidator
from flow.providers.base import (
    CLIConfig,
    ConnectionMethod,
    EnvVarSpec,
    PricingModel,
    ProviderCapabilities,
    ProviderManifest,
    ValidationRules,
)


class TestProviderResolverIntegration:
    """Test ProviderResolver with real manifests."""
    
    def test_fcp_manifest_loading(self):
        """Test loading FCP manifest."""
        manifest = ProviderResolver.get_manifest("fcp")
        
        assert manifest.name == "fcp"
        assert manifest.display_name == "Flow Compute Platform"
        assert manifest.capabilities.pricing_model == PricingModel.MARKET
        assert manifest.cli_config.default_region == "us-central1-a"
    
    def test_mount_pattern_resolution(self):
        """Test mount pattern resolution using FCP manifest."""
        # S3 mount
        path = ProviderResolver.resolve_mount_path("fcp", "s3://bucket/data")
        assert path == "/data"
        
        # Volume mount
        path = ProviderResolver.resolve_mount_path("fcp", "volume://my-volume")
        assert path == "/mnt"
        
        # GCS mount
        path = ProviderResolver.resolve_mount_path("fcp", "gs://bucket/data")
        assert path == "/gcs"
        
        # HTTPS mount
        path = ProviderResolver.resolve_mount_path("fcp", "https://example.com/file.tar.gz")
        assert path == "/downloads"
        
        # Unknown pattern fallback
        path = ProviderResolver.resolve_mount_path("fcp", "/local/path")
        assert path == "/mnt/path"
    
    def test_connection_command_generation(self):
        """Test SSH connection command generation."""
        # Create mock task with SSH details
        mock_task = MagicMock()
        mock_task.ssh_host = "example.com"
        mock_task.ssh_port = 2222
        mock_task.ssh_user = "ubuntu"
        
        command = ProviderResolver.get_connection_command("fcp", mock_task)
        assert command == "ssh -p 2222 ubuntu@example.com"
    
    def test_validation_rules(self):
        """Test provider-specific validation rules."""
        # Valid FCP API key
        assert ProviderResolver.validate_config_value("fcp", "api_key", "fkey_12345678901234567890") is True
        
        # Invalid FCP API key
        assert ProviderResolver.validate_config_value("fcp", "api_key", "bad_key") is False
        
        # Valid region
        assert ProviderResolver.validate_config_value("fcp", "region", "us-central1-a") is True
        
        # Invalid region
        assert ProviderResolver.validate_config_value("fcp", "region", "invalid-region") is False
        
        # Valid project name
        assert ProviderResolver.validate_config_value("fcp", "project", "my-project-123") is True
        
        # Invalid project name
        assert ProviderResolver.validate_config_value("fcp", "project", "My Project!") is False
    
    def test_env_var_mapping(self):
        """Test environment variable name mapping."""
        env_vars = ProviderResolver.get_env_vars("fcp")
        
        assert env_vars["api_key"] == "FCP_API_KEY"
        assert env_vars["project"] == "FCP_PROJECT"
        assert env_vars["region"] == "FCP_REGION"


class TestCLICommandsWithManifest:
    """Test CLI commands using provider manifest system."""
    
    @pytest.fixture
    def mock_flow(self):
        """Create mock Flow client."""
        with patch("flow.cli.commands.run.Flow") as MockFlow:
            mock_instance = MagicMock()
            mock_instance.provider = MagicMock()
            mock_instance.provider.__class__.__name__ = "FCPProvider"
            MockFlow.return_value = mock_instance
            yield mock_instance
    
    def test_run_command_mount_resolution(self, mock_flow, tmp_path):
        """Test run command uses provider resolver for mounts."""
        # Create test config file
        config_file = tmp_path / "test.yaml"
        config_file.write_text("""
name: test-task
instance_type: a100
command: echo hello
""")
        
        # Mock task submission
        mock_task = MagicMock()
        mock_task.task_id = "task-123"
        mock_flow.run.return_value = mock_task
        
        # Execute run command with mounts
        cmd = RunCommand()
        cmd._execute(
            str(config_file),
            wait=False,
            dry_run=False,
            watch=False,
            output_json=True,
            mount=("s3://bucket/data", "volume://my-vol", "gs://bucket/file")
        )
        
        # Verify mounts were resolved using provider patterns
        call_args = mock_flow.run.call_args
        config = call_args[0][0]
        mounts = call_args[1]["mounts"]
        
        # Check mount paths match FCP manifest patterns
        assert mounts["/data"] == "s3://bucket/data"
        assert mounts["/mnt"] == "volume://my-vol"
        assert mounts["/gcs"] == "gs://bucket/file"
    
    @pytest.mark.asyncio
    async def test_init_command_validation(self):
        """Test init command uses provider resolver for validation."""
        cmd = InitCommand()
        
        # Test with valid FCP values
        with patch("flow.cli.commands.init.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp/test")
            with patch("builtins.open", create=True) as mock_open:
                await cmd._configure_with_options(
                    provider="fcp",
                    api_key="fkey_12345678901234567890",
                    project="my-project",
                    region="us-central1-a",
                    api_url=None,
                    dry_run=True
                )
        
        # Should complete without errors
    
    def test_ssh_command_connection_format(self, tmp_path):
        """Test SSH command uses provider-specific connection format."""
        # Create mock task with SSH access
        mock_task = MagicMock()
        mock_task.task_id = "task-123"
        mock_task.ssh_host = "example.com"
        mock_task.ssh_port = 22
        mock_task.ssh_user = "ubuntu"
        
        # Create mock Flow client
        mock_flow = MagicMock()
        mock_flow.provider = MagicMock()
        mock_flow.provider.__class__.__name__ = "FCPProvider"
        
        cmd = SSHCommand()
        
        # Capture console output
        with patch("flow.cli.commands.ssh.console") as mock_console:
            cmd.execute_on_task(mock_task, mock_flow)
        
        # Verify provider-specific connection command was shown
        mock_console.print.assert_any_call("\n[bold]Connect with:[/bold]")
        mock_console.print.assert_any_call("  ssh -p 22 ubuntu@example.com\n")


class TestConfigValidatorWithManifest:
    """Test config validator using provider manifest."""
    
    def test_provider_specific_validation(self):
        """Test validation uses provider-specific rules."""
        validator = ConfigValidator(provider="fcp")
        
        # Valid FCP API key
        result = validator.validate_api_key_format("fkey_12345678901234567890")
        assert result.status.value == "valid"
        
        # Invalid FCP API key
        result = validator.validate_api_key_format("invalid_key")
        assert result.status.value == "invalid"
        assert "fcp" in result.message.lower()
        
        # Valid project
        result = validator.validate_project_name("my-project-123")
        assert result.status.value == "valid"
        
        # Invalid project
        result = validator.validate_project_name("My Project!")
        assert result.status.value == "invalid"
        
        # Valid region
        result = validator.validate_region("us-central1-a")
        assert result.status.value == "valid"
        
        # Invalid region
        result = validator.validate_region("invalid-region")
        assert result.status.value == "invalid"
    
    def test_validate_all_with_provider(self):
        """Test validate_all uses provider from config."""
        validator = ConfigValidator()
        
        config = {
            "provider": "fcp",
            "api_key": "fkey_12345678901234567890",
            "project": "my-project",
            "region": "us-central1-a"
        }
        
        valid, errors = validator.validate_all(config)
        assert valid is True
        assert len(errors) == 0
        
        # Test with invalid values
        config = {
            "provider": "fcp",
            "api_key": "bad_key",
            "project": "Bad Project!",
            "region": "invalid"
        }
        
        valid, errors = validator.validate_all(config)
        assert valid is False
        assert len(errors) == 3  # api_key, project, region


class TestManifestMigration:
    """Test migration from hardcoded to manifest-based behavior."""
    
    def test_no_hardcoded_fcp_logic(self):
        """Ensure no FCP-specific logic remains in CLI commands."""
        # Check run.py doesn't have hardcoded mount patterns
        run_path = Path(__file__).parent.parent.parent / "src/flow/cli/commands/run.py"
        if run_path.exists():
            content = run_path.read_text()
            assert 's3://' not in content or 'ProviderResolver' in content
            assert 'volume://' not in content or 'ProviderResolver' in content
        
        # Check init.py doesn't have hardcoded env vars
        init_path = Path(__file__).parent.parent.parent / "src/flow/cli/commands/init.py"
        if init_path.exists():
            content = init_path.read_text()
            assert 'FCP_API_KEY' not in content or 'ProviderResolver' in content
            assert 'FCP_PROJECT' not in content or 'ProviderResolver' in content
    
    def test_manifest_defines_all_behavior(self):
        """Test that all FCP behavior is defined in manifest."""
        manifest = ProviderResolver.get_manifest("fcp")
        
        # Check all necessary fields are defined
        assert manifest.cli_config.env_vars  # Has env var definitions
        assert manifest.cli_config.mount_patterns  # Has mount patterns
        assert manifest.cli_config.connection_method  # Has SSH config
        assert manifest.cli_config.config_fields  # Has config fields
        assert manifest.validation  # Has validation rules
        
        # Check specific FCP behaviors are captured
        env_var_names = [ev.name for ev in manifest.cli_config.env_vars]
        assert "FCP_API_KEY" in env_var_names
        assert "FCP_PROJECT" in env_var_names
        assert "FCP_REGION" in env_var_names
        
        # Check mount patterns
        assert r"^s3://.*" in manifest.cli_config.mount_patterns
        assert r"^volume://.*" in manifest.cli_config.mount_patterns