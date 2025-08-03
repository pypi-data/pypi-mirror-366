"""Integration tests for CLI mount functionality."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml
from click.testing import CliRunner

from flow.api.models import Task, TaskStatus
from datetime import datetime, timezone
from flow.cli.app import cli


class TestCLIMounts:
    """Test CLI --mount flag functionality."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment for consistent test output."""
        # Use simple output mode for consistent test assertions
        old_env = os.environ.get('FLOW_SIMPLE_OUTPUT')
        os.environ['FLOW_SIMPLE_OUTPUT'] = '1'
        yield
        # Restore original value
        if old_env is None:
            os.environ.pop('FLOW_SIMPLE_OUTPUT', None)
        else:
            os.environ['FLOW_SIMPLE_OUTPUT'] = old_env
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()

    @pytest.fixture
    def task_yaml(self):
        """Create temporary task YAML file."""
        config = {
            "name": "test-task",
            "instance_type": "a100",
            "command": "echo hello"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            yield f.name

        # Cleanup
        Path(f.name).unlink()

    @pytest.fixture
    def mock_flow(self):
        """Mock Flow client."""
        mock_task = Task(
            task_id="task-789",
            name="test-task",
            status=TaskStatus.RUNNING,
            instance_type="a100",
            region="us-east-1",
            created_at=datetime.now(timezone.utc),
            num_instances=1,
            cost_per_hour="$5.00"
        )

        mock_flow = Mock()
        mock_flow.run = Mock(return_value=mock_task)
        mock_flow.get_task = Mock(return_value=mock_task)
        return mock_flow

    def test_run_with_single_mount(self, runner, task_yaml, mock_flow):
        """Test run command with single --mount flag."""
        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--mount', 's3://my-bucket/data',
                '--no-wait'
            ])

        print(f"Exit code: {result.exit_code}")
        print(f"Output: {result.output}")
        print(f"Exception: {result.exception}")
        assert result.exit_code == 0
        assert "Task submitted successfully!" in result.output or "Task Submitted" in result.output

        # Verify Flow.run was called with mounts
        mock_flow.run.assert_called_once()
        call_args = mock_flow.run.call_args
        assert call_args[1]['mounts'] == {'/data': 's3://my-bucket/data'}

    def test_run_with_mount_target_syntax(self, runner, task_yaml, mock_flow):
        """Test run with target=source mount syntax."""
        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--mount', '/data=s3://my-bucket/datasets',
                '--no-wait'
            ])

        assert result.exit_code == 0

        # Verify mount was parsed correctly
        call_args = mock_flow.run.call_args
        assert call_args[1]['mounts'] == {'/data': 's3://my-bucket/datasets'}

    def test_run_with_multiple_mounts(self, runner, task_yaml, mock_flow):
        """Test run with multiple --mount flags."""
        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--mount', '/data=s3://bucket/data',
                '--mount', '/models=s3://bucket/models',
                '--mount', '/checkpoints=volume://ckpt-vol',
                '--no-wait'
            ])

        assert result.exit_code == 0

        # Verify all mounts were parsed
        call_args = mock_flow.run.call_args
        mounts = call_args[1]['mounts']
        assert mounts == {
            '/data': 's3://bucket/data',
            '/models': 's3://bucket/models',
            '/checkpoints': 'volume://ckpt-vol'
        }

    def test_run_mount_dry_run(self, runner, task_yaml):
        """Test --dry-run displays mount information."""
        result = runner.invoke(cli, [
            'run', task_yaml,
            '--mount', '/data=s3://bucket/dataset',
            '--mount', 'volume://my-vol',
            '--dry-run'
        ])

        assert result.exit_code == 0
        assert "Task Configuration" in result.output
        assert "Mounts:" in result.output
        assert "/data → s3://bucket/dataset" in result.output
        assert "/mnt → volume://my-vol" in result.output
        assert "✓ Configuration is valid" in result.output

    def test_run_json_output_with_mounts(self, runner, task_yaml, mock_flow):
        """Test JSON output includes task info (mounts are internal)."""
        # Update mock to have proper attributes
        mock_flow.run.return_value.ssh_command = None

        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--mount', 's3://bucket/data',
                '--json',
                '--no-wait'
            ])

        assert result.exit_code == 0

        # Parse JSON output
        output = json.loads(result.output)
        assert output['task_id'] == 'task-789'
        assert output['status'] == 'submitted'

    def test_run_without_mounts(self, runner, task_yaml, mock_flow):
        """Test run without --mount flags works normally."""
        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--no-wait'
            ])

        assert result.exit_code == 0

        # Verify Flow.run was called without mounts
        call_args = mock_flow.run.call_args
        assert call_args[1]['mounts'] is None

    def test_run_mount_with_equals_in_path(self, runner, task_yaml, mock_flow):
        """Test mount with equals sign in the source path."""
        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--mount', '/data=s3://bucket/path=with=equals',
                '--no-wait'
            ])

        assert result.exit_code == 0

        # Verify only first = was used as separator
        call_args = mock_flow.run.call_args
        assert call_args[1]['mounts'] == {'/data': 's3://bucket/path=with=equals'}

    def test_run_mount_complex_paths(self, runner, task_yaml, mock_flow):
        """Test various complex mount paths."""
        with patch('flow.cli.commands.run.Flow', return_value=mock_flow):
            result = runner.invoke(cli, [
                'run', task_yaml,
                '--mount', '/mnt/data=s3://bucket/datasets/imagenet/2024',
                '--mount', '/home/user/models=volume://user-models',
                '--mount', '/var/cache=s3://cache-bucket/ml-cache',
                '--no-wait'
            ])

        assert result.exit_code == 0

        # Verify complex paths handled correctly
        call_args = mock_flow.run.call_args
        mounts = call_args[1]['mounts']
        assert mounts['/mnt/data'] == 's3://bucket/datasets/imagenet/2024'
        assert mounts['/home/user/models'] == 'volume://user-models'
        assert mounts['/var/cache'] == 's3://cache-bucket/ml-cache'
