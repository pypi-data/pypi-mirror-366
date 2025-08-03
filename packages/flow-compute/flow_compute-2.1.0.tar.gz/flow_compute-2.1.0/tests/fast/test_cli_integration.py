"""Test CLI integration for Flow SDK - minimal tests without overmocking."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from flow.cli.app import cli


class TestCLIIntegration:
    """Test basic CLI functionality without complex mocking."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    def test_cli_help(self, runner):
        """Test that CLI help works."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Flow CLI - Submit and manage GPU tasks' in result.output

    def test_cli_version(self, runner):
        """Test that CLI version works."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '2.0.0' in result.output

    def test_cli_invalid_command(self, runner):
        """Test that invalid commands fail gracefully."""
        result = runner.invoke(cli, ['nonexistent-command'])
        assert result.exit_code != 0
        assert 'Error' in result.output or 'No such command' in result.output

    def test_cli_run_missing_file(self, runner):
        """Test run command with missing file."""
        result = runner.invoke(cli, ['run', '/nonexistent/file.yaml'])
        assert result.exit_code != 0

    @pytest.mark.parametrize("invalid_config", [
        {},  # Empty config
        {'name': 'test'},  # Missing required fields
        {'name': 'test', 'instance_type': 'a100'},  # Missing command
    ])
    def test_cli_run_invalid_yaml(self, runner, invalid_config):
        """Test run command with invalid YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            config_file = Path(f.name)

        try:
            result = runner.invoke(cli, ['run', str(config_file)])
            # Should fail with validation error
            assert result.exit_code != 0
        finally:
            config_file.unlink(missing_ok=True)
