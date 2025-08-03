"""Unit tests for CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml
from click.testing import CliRunner

from flow.api.models import TaskConfig
from flow.cli.app import cli



class TestCLIExampleCommand:
    """Test 'flow example' command."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_example_list_all(self, runner):
        """Test listing all available examples.
        
        GIVEN: User runs 'flow example' without arguments
        WHEN: Command executes
        THEN: All available examples are listed
        """
        result = runner.invoke(cli, ['example'])

        assert result.exit_code == 0
        assert "Available examples:" in result.output
        assert "minimal" in result.output
        assert "gpu-test" in result.output
        assert "system-info" in result.output
        assert "training" in result.output
        assert "flow example <name>" in result.output

    def test_example_show_minimal(self, runner):
        """Test showing minimal example.
        
        GIVEN: User runs 'flow example minimal'
        WHEN: Command executes
        THEN: Minimal example YAML is output
        """
        result = runner.invoke(cli, ['example', 'minimal', '--show'])

        assert result.exit_code == 0
        # Parse output as YAML to verify it's valid
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'minimal-example'
        assert output_yaml['instance_type'] == '8xh100'
        assert 'Hello from Flow SDK!' in output_yaml['command']
        assert 'hostname' in output_yaml['command']

    def test_example_show_gpu_test(self, runner):
        """Test showing GPU test example.
        
        GIVEN: User runs 'flow example gpu-test'
        WHEN: Command executes
        THEN: GPU test example YAML is output
        """
        result = runner.invoke(cli, ['example', 'gpu-test', '--show'])

        assert result.exit_code == 0
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'gpu-test'
        assert output_yaml['instance_type'] == '8xh100'
        assert 'nvidia-smi' in output_yaml['command']
        assert output_yaml['max_price_per_hour'] == 15.0

    def test_example_show_system_info(self, runner):
        """Test showing system info example.
        
        GIVEN: User runs 'flow example system-info'
        WHEN: Command executes
        THEN: System info example YAML is output
        """
        result = runner.invoke(cli, ['example', 'system-info', '--show'])

        assert result.exit_code == 0
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'system-info'
        assert output_yaml['instance_type'] == '8xh100'
        assert 'System Information' in output_yaml['command']
        assert 'nvidia-smi' in output_yaml['command']
        # Examples don't have resources field anymore

    def test_example_show_training(self, runner):
        """Test showing training example.
        
        GIVEN: User runs 'flow example training'
        WHEN: Command executes
        THEN: Notebook example YAML is output with ports
        """
        result = runner.invoke(cli, ['example', 'training', '--show'])

        assert result.exit_code == 0
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'basic-training'
        assert output_yaml['instance_type'] == '8xh100'
        assert 'Starting training job' in output_yaml['command']
        assert len(output_yaml.get('volumes', [])) == 2
        assert output_yaml['max_price_per_hour'] == 10.0

    def test_example_invalid_name(self, runner):
        """Test requesting invalid example.
        
        GIVEN: User runs 'flow example invalid'
        WHEN: Command executes
        THEN: Error is shown with available examples
        """
        result = runner.invoke(cli, ['example', 'invalid'])

        assert result.exit_code == 1
        assert "Unknown example: invalid" in result.output
        assert "Available: " in result.output
        assert "minimal" in result.output
        assert "gpu-test" in result.output
        assert "training" in result.output

    def test_example_output_redirection(self, runner, tmp_path):
        """Test example output can be redirected to file.
        
        GIVEN: User runs 'flow example minimal > config.yaml'
        WHEN: Output is captured
        THEN: Valid YAML can be saved
        """
        result = runner.invoke(cli, ['example', 'minimal', '--show'])

        assert result.exit_code == 0

        # Save to file
        config_file = tmp_path / "config.yaml"
        config_file.write_text(result.output)

        # Verify it can be loaded as TaskConfig
        config = TaskConfig.from_yaml(str(config_file))
        assert config.name == 'minimal-example'
        # Just check that it can be loaded
        assert config.instance_type == '8xh100'
        assert 'Hello from Flow SDK!' in config.command


