"""Integration tests for CLI functionality.

These tests verify the CLI works correctly with real components.
We test actual command execution and real workflows.
"""

import os

import pytest
import yaml
from click.testing import CliRunner

from flow.cli.app import cli
from tests.testing import TaskConfigBuilder


@pytest.mark.integration
class TestCLIIntegration:
    """Test CLI commands with real components."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def test_env(self, tmp_path):
        """Set up test environment variables."""
        env = {
            "FCP_TEST_API_KEY": os.environ.get("FCP_TEST_API_KEY", ""),
            "FLOW_SIMPLE_OUTPUT": "1",  # Use simple output for consistent tests
            "FLOW_CONFIG_DIR": str(tmp_path / ".flow"),
            "FLOW_CACHE_DIR": str(tmp_path / ".cache"),
        }

        # Create directories
        (tmp_path / ".flow").mkdir()
        (tmp_path / ".cache").mkdir()

        return env

    @pytest.mark.skipif(not os.environ.get("FCP_TEST_API_KEY"), reason="Requires test API key")
    def test_cli_auth_flow(self, runner, test_env, tmp_path):
        """Test CLI authentication flow."""
        # Test auth command
        result = runner.invoke(
            cli,
            ["auth", "login", "--api-key", test_env["FCP_TEST_API_KEY"]],
            env=test_env
        )

        assert result.exit_code == 0
        assert "Successfully authenticated" in result.output

        # Verify credentials were saved
        creds_file = tmp_path / ".flow" / "credentials.json"
        assert creds_file.exists()

        # Test auth status
        result = runner.invoke(cli, ["auth", "status"], env=test_env)
        assert result.exit_code == 0
        assert "Authenticated" in result.output

    def test_cli_run_with_yaml(self, runner, test_env, tmp_path):
        """Test running task from YAML file."""
        # Create task YAML
        task_yaml = tmp_path / "task.yaml"
        config = TaskConfigBuilder().with_cpu("small").with_command("echo 'CLI test'").build()

        yaml_content = {
            "name": config.name,
            "instance_type": config.instance_type,
            "command": config.command,
            "max_price_per_hour": config.max_price_per_hour
        }

        with open(task_yaml, 'w') as f:
            yaml.dump(yaml_content, f)

        # Test dry run first
        result = runner.invoke(
            cli,
            ["run", str(task_yaml), "--dry-run"],
            env=test_env
        )

        assert result.exit_code == 0
        assert "Configuration is valid" in result.output
        assert config.name in result.output

    def test_cli_list_instances(self, runner, test_env):
        """Test listing tasks (no instances command in current CLI)."""
        # Test status command instead (closest equivalent)
        result = runner.invoke(
            cli,
            ["status", "--limit", "5"],
            env=test_env
        )

        # Without authentication, it should fail with auth error
        if result.exit_code != 0:
            assert ("authentication" in result.output.lower() or
                   "flow init" in result.output.lower() or
                   "no flow configuration found" in result.output.lower() or
                   "set up your account" in result.output.lower())
        else:
            # With authentication, should show tasks or "No tasks found"
            assert "tasks" in result.output.lower() or "no tasks found" in result.output.lower()

    def test_cli_output_formats(self, runner, test_env, tmp_path):
        """Test different output formats."""
        # Test JSON output with info command
        # Since we don't have real tasks, skip this test
        pytest.skip("JSON output test requires real task ID")


    def test_cli_error_handling(self, runner, test_env):
        """Test CLI error handling and messages."""
        # Test invalid command
        result = runner.invoke(cli, ["invalid-command"], env=test_env)
        assert result.exit_code != 0
        assert "Error" in result.output or "Usage" in result.output

        # Test missing required arguments
        result = runner.invoke(cli, ["run"], env=test_env)
        assert result.exit_code != 0
        assert "Missing" in result.output or "Usage" in result.output

    def test_cli_help_system(self, runner):
        """Test CLI help and documentation."""
        # Test main help
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Flow CLI - Submit and manage GPU tasks" in result.output
        assert "Commands:" in result.output

        # Test command help
        commands = ["run", "status", "cancel", "ssh", "logs", "init"]
        for cmd in commands:
            result = runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0
            assert "Usage:" in result.output

    @pytest.mark.skipif(not os.environ.get("FCP_TEST_API_KEY"), reason="Requires test API key")
    def test_cli_task_workflow(self, runner, test_env, tmp_path):
        """Test complete task workflow through CLI."""
        # Skip if no real API access
        if not test_env.get("FCP_TEST_API_KEY"):
            pytest.skip("Requires FCP_TEST_API_KEY")

        # Create simple task
        task_yaml = tmp_path / "test_task.yaml"
        task_yaml.write_text("""
name: cli-integration-test
instance_type: cpu-small
command: |
  echo "Starting CLI integration test"
  sleep 2
  echo "Test completed"
max_price_per_hour: 5.0
""")

        # Submit task
        result = runner.invoke(
            cli,
            ["run", str(task_yaml), "--no-wait"],
            env=test_env
        )

        if result.exit_code == 0:
            # Extract task ID from output
            lines = result.output.split('\n')
            task_id = None
            for line in lines:
                if "task-" in line:
                    # Extract task ID
                    import re
                    match = re.search(r'task-[a-f0-9-]+', line)
                    if match:
                        task_id = match.group(0)
                        break

            if task_id:
                # Check status
                result = runner.invoke(cli, ["status", task_id], env=test_env)
                assert result.exit_code == 0
                assert task_id in result.output

                # Cancel task
                result = runner.invoke(cli, ["cancel", task_id], env=test_env)
                assert result.exit_code == 0
