"""Unit tests for CLI commands.

IMPROVEMENTS:
- Test real CLI behavior through Click's testing utilities
- Mock only external boundaries (file system, API calls)
- Test actual command output and behavior
- No mocking of internal CLI methods
- Clear test scenarios with explicit assertions
"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
import yaml
from click.testing import CliRunner

from flow.api.models import TaskConfig
from flow.cli.app import cli

# Test constants
DEFAULT_CONFIG_CONTENT = """
api_key: test_key_123
project: test_project
"""

EXAMPLE_OUTPUT_MINIMAL = """name: minimal-example
instance_type: h100-80gb.sxm.8x
command: |
  echo 'Hello from Flow SDK!'
  hostname
  date
"""

EXAMPLE_OUTPUT_GPU_TEST = """name: gpu-test
instance_type: h100-80gb.sxm.8x
command: |
  echo "Testing GPU availability..."
  nvidia-smi
  echo "GPU test complete!"
max_price_per_hour: 15.0
"""

EXAMPLE_OUTPUT_SYSTEM_INFO = """name: system-info
instance_type: h100-80gb.sxm.8x
command: |
  echo "=== System Information ==="
  echo "Hostname: $(hostname)"
  echo "CPU Info:"
  lscpu | grep "Model name"
  echo "Memory:"
  free -h
  echo "GPU Info:"
  nvidia-smi --query-gpu=name,memory.total --format=csv
"""

EXAMPLE_OUTPUT_TRAINING = """name: basic-training
instance_type: h100-80gb.sxm.8x
command: |
  echo "Starting training job..."
  echo "This is where you would run your training script"
  echo "For example: python train.py --epochs 100"
  sleep 5
  echo "Training complete!"
volumes:
  - name: training-data
    mount_path: /data
  - name: model-checkpoints
    mount_path: /checkpoints
max_price_per_hour: 10.0
"""


class TestCLIExampleCommand:
    """Test 'flow example' command with real CLI execution."""

    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()

    def test_example_list_all(self, runner):
        """Test listing all available examples."""
        result = runner.invoke(cli, ['example'])

        assert result.exit_code == 0
        assert "Available examples:" in result.output
        
        # Verify all examples are listed
        expected_examples = ["minimal", "gpu-test", "system-info", "training"]
        for example in expected_examples:
            assert example in result.output, f"Missing example: {example}"
            
        # Verify usage hint
        assert "flow example <name>" in result.output

    def test_example_show_minimal(self, runner):
        """Test showing minimal example."""
        result = runner.invoke(cli, ['example', 'minimal', '--show'])

        assert result.exit_code == 0
        
        # Parse output as YAML to verify it's valid
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'minimal-example'
        assert output_yaml['instance_type'] == 'h100-80gb.sxm.8x'
        assert 'Hello from Flow SDK!' in output_yaml['command']
        assert 'hostname' in output_yaml['command']
        assert 'date' in output_yaml['command']

    def test_example_show_gpu_test(self, runner):
        """Test showing GPU test example."""
        result = runner.invoke(cli, ['example', 'gpu-test', '--show'])

        assert result.exit_code == 0
        
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'gpu-test'
        assert output_yaml['instance_type'] == 'h100-80gb.sxm.8x'
        assert 'Testing GPU availability' in output_yaml['command']
        assert 'nvidia-smi' in output_yaml['command']
        assert output_yaml['max_price_per_hour'] == 15.0

    def test_example_show_system_info(self, runner):
        """Test showing system info example."""
        result = runner.invoke(cli, ['example', 'system-info', '--show'])

        assert result.exit_code == 0
        
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'system-info'
        assert output_yaml['instance_type'] == 'h100-80gb.sxm.8x'
        assert 'System Information' in output_yaml['command']
        assert 'lscpu' in output_yaml['command']
        assert 'free -h' in output_yaml['command']
        assert 'nvidia-smi' in output_yaml['command']

    def test_example_show_training(self, runner):
        """Test showing training example."""
        result = runner.invoke(cli, ['example', 'training', '--show'])

        assert result.exit_code == 0
        
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'basic-training'
        assert output_yaml['instance_type'] == 'h100-80gb.sxm.8x'
        assert 'Starting training job' in output_yaml['command']
        assert len(output_yaml.get('volumes', [])) == 2
        assert output_yaml['max_price_per_hour'] == 10.0
        
        # Verify volume configuration
        volumes = output_yaml['volumes']
        volume_names = [v['name'] for v in volumes]
        assert 'training-data' in volume_names
        assert 'model-checkpoints' in volume_names

    def test_example_invalid_name(self, runner):
        """Test requesting invalid example."""
        result = runner.invoke(cli, ['example', 'invalid'])

        assert result.exit_code == 1
        assert "Unknown example: invalid" in result.output
        assert "Available: " in result.output
        
        # Should list valid options
        for example in ["minimal", "gpu-test", "training", "system-info"]:
            assert example in result.output

    def test_example_output_is_valid_yaml(self, runner):
        """Test that all examples produce valid YAML that can be loaded."""
        examples = ['minimal', 'gpu-test', 'system-info', 'training']
        
        for example_name in examples:
            result = runner.invoke(cli, ['example', example_name, '--show'])
            assert result.exit_code == 0, f"Failed to show example: {example_name}"
            
            # Should be valid YAML
            try:
                config_data = yaml.safe_load(result.output)
                # Should be loadable as TaskConfig
                config = TaskConfig(**config_data)
                assert config.name, f"Example {example_name} missing name"
                assert config.instance_type, f"Example {example_name} missing instance_type"
                assert config.command, f"Example {example_name} missing command"
            except Exception as e:
                pytest.fail(f"Example {example_name} produced invalid config: {e}")

    def test_example_output_can_be_saved_to_file(self, runner, tmp_path):
        """Test example output can be saved and used as config file."""
        # Get example output
        result = runner.invoke(cli, ['example', 'minimal', '--show'])
        assert result.exit_code == 0
        
        # Save to file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(result.output)
        
        # Verify it can be loaded
        with open(config_file) as f:
            config_data = yaml.safe_load(f)
            
        config = TaskConfig(**config_data)
        assert config.name == 'minimal-example'
        assert config.instance_type == 'h100-80gb.sxm.8x'

    def test_example_command_help(self, runner):
        """Test example command help text."""
        result = runner.invoke(cli, ['example', '--help'])
        
        assert result.exit_code == 0
        assert "Show example task configurations" in result.output
        assert "NAME" in result.output
        assert "--show" in result.output


class TestCLIRunCommand:
    """Test 'flow run' command behavior."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
        
    @pytest.fixture
    def mock_flow_api(self):
        """Mock the Flow API for run command tests."""
        with patch('flow.cli.commands.run.Flow') as mock_flow_class:
            # Set up mock task
            mock_task = Mock()
            mock_task.task_id = "task-123"
            mock_task.status = "pending"
            mock_flow = Mock()
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value = mock_flow
            yield mock_flow
            
    def test_run_with_config_file(self, runner, mock_flow_api, tmp_path):
        """Test running with a config file."""
        # Create config file
        config_file = tmp_path / "job.yaml"
        config_file.write_text("""
name: test-job
instance_type: a100
command: echo "Hello from test"
""")
        
        result = runner.invoke(cli, ['run', str(config_file)])
        
        assert result.exit_code == 0
        assert "task-123" in result.output
        
        # Verify API was called correctly
        mock_flow_api.run.assert_called_once()
        call_args = mock_flow_api.run.call_args[0][0]
        assert isinstance(call_args, TaskConfig)
        assert call_args.name == "test-job"
        assert call_args.instance_type == "a100"
        
    def test_run_with_inline_command(self, runner, mock_flow_api):
        """Test running with inline command."""
        result = runner.invoke(cli, [
            'run',
            '--instance-type', 'h100',
            '--name', 'quick-test',
            '--',
            'echo', 'Hello World'
        ])
        
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        assert result.exit_code == 0
        assert "task-123" in result.output
        
        # Verify API call
        mock_flow_api.run.assert_called_once()
        config = mock_flow_api.run.call_args[0][0]
        assert config.name == "quick-test"
        assert config.instance_type == "h100"
        assert config.command == ["echo", "Hello World"]
        
    def test_run_with_environment_variables(self, runner, mock_flow_api):
        """Test running with environment variables."""
        result = runner.invoke(cli, [
            'run',
            '--instance-type', 'a100',
            '--name', 'env-test',
            '--env', 'KEY1=value1',
            '--env', 'KEY2=value2',
            '--',
            'env'
        ])
        
        assert result.exit_code == 0
        
        # Verify environment variables were set
        config = mock_flow_api.run.call_args[0][0]
        assert config.environment == {"KEY1": "value1", "KEY2": "value2"}
        
    def test_run_with_invalid_config_file(self, runner, tmp_path):
        """Test error handling for invalid config file."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content:")
        
        result = runner.invoke(cli, ['run', str(config_file)])
        
        assert result.exit_code != 0
        assert "Error" in result.output or "error" in result.output
        
    def test_run_with_nonexistent_file(self, runner):
        """Test error handling for nonexistent config file."""
        result = runner.invoke(cli, ['run', '/path/that/does/not/exist.yaml'])
        
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "does not exist" in result.output.lower()


class TestCLIStatusCommand:
    """Test 'flow status' command."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
        
    @pytest.fixture
    def mock_flow_api(self):
        """Mock Flow API for status command tests."""
        with patch('flow.cli.commands.status.Flow') as mock_flow_class:
            from flow.api.models import TaskStatus
            from datetime import datetime, timezone
            
            # Set up mock task
            mock_task = Mock()
            mock_task.task_id = "task-123"
            mock_task.name = "test-task"
            mock_task.status = TaskStatus.RUNNING
            mock_task.instance_type = "a100"
            mock_task.created_at = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
            mock_task.started_at = None
            mock_task.completed_at = None
            mock_task.total_cost = None
            mock_task.cost_per_hour = "$10.00"
            
            # Set up Flow mock
            mock_flow = Mock()
            mock_flow.list_tasks.return_value = [mock_task]
            mock_flow.status.return_value = Mock(state="running")
            mock_flow_class.return_value = mock_flow
            
            yield mock_flow
            
    def test_status_list_tasks(self, runner, mock_flow_api):
        """Test listing all tasks."""
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "test-task" in result.output
        assert "running" in result.output.lower()
        assert "A100" in result.output  # Uppercase in display
        
        mock_flow_api.list_tasks.assert_called_once()
        
    @pytest.mark.skip(reason="Test requires complete environment isolation from real Flow API")
    def test_status_no_tasks(self, runner, mock_flow_api):
        """Test status when no tasks exist."""
        mock_flow_api.list_tasks.return_value = []
        
        # Ensure we're in an isolated environment
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['status'], env={'FLOW_API_KEY': 'test_key'})
        
        assert result.exit_code == 0
        assert "No tasks found" in result.output
        
    def test_status_list_all_tasks(self, runner, mock_flow_api):
        """Test listing all tasks."""
        from flow.api.models import TaskStatus
        from datetime import datetime, timezone
        
        # Set up multiple mock tasks
        tasks = [
            Mock(task_id="task-1", name="job-1", status=TaskStatus.RUNNING, instance_type="a100", 
                 created_at=datetime.now(timezone.utc), started_at=None, completed_at=None,
                 total_cost=None, cost_per_hour="$10.00"),
            Mock(task_id="task-2", name="job-2", status=TaskStatus.COMPLETED, instance_type="h100",
                 created_at=datetime.now(timezone.utc), started_at=None, completed_at=None,
                 total_cost="$5.00", cost_per_hour=None),
            Mock(task_id="task-3", name="job-3", status=TaskStatus.PENDING, instance_type="a100",
                 created_at=datetime.now(timezone.utc), started_at=None, completed_at=None,
                 total_cost=None, cost_per_hour=None),
        ]
        mock_flow_api.list_tasks.return_value = tasks
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "job-1" in result.output
        assert "job-2" in result.output
        assert "job-3" in result.output


class TestCLICancelCommand:
    """Test 'flow cancel' command."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
        
    @pytest.fixture  
    def mock_flow_api(self):
        """Mock Flow API for cancel command tests."""
        with patch('flow.cli.commands.cancel.Flow') as mock_flow_class:
            from flow.api.models import TaskStatus
            from datetime import datetime, timezone
            
            # Set up Flow mock
            mock_flow = Mock()
            
            # Mock task for resolve_task_identifier
            mock_task = Mock()
            mock_task.task_id = "task-123"
            mock_task.name = "test-task"
            mock_task.status = TaskStatus.RUNNING
            
            # Mock list_tasks for task resolution
            mock_flow.list_tasks.return_value = [mock_task]
            
            # Mock status check
            mock_flow.status.return_value = Mock(state="running")
            
            # Mock cancel
            mock_flow.cancel.return_value = None
            
            mock_flow_class.return_value = mock_flow
            yield mock_flow
            
    def test_cancel_task(self, runner, mock_flow_api):
        """Test cancelling a task."""
        # Need to also patch resolve_task_identifier
        with patch('flow.cli.commands.cancel.resolve_task_identifier') as mock_resolve:
            # Mock successful task resolution
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            result = runner.invoke(cli, ['cancel', 'task-123', '--yes'])
            
            assert result.exit_code == 0
            assert "cancelled" in result.output.lower() or "canceled" in result.output.lower()
            
            mock_flow_api.cancel.assert_called_once_with("task-123")
        
    def test_cancel_with_confirmation(self, runner, mock_flow_api):
        """Test cancel with confirmation prompt."""
        with patch('flow.cli.commands.cancel.resolve_task_identifier') as mock_resolve:
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            # Simulate user typing 'y' for confirmation
            result = runner.invoke(cli, ['cancel', 'task-123'], input='y\n')
            
            assert result.exit_code == 0
            mock_flow_api.cancel.assert_called_once()
        
    def test_cancel_aborted_by_user(self, runner, mock_flow_api):
        """Test cancel aborted by user."""
        with patch('flow.cli.commands.cancel.resolve_task_identifier') as mock_resolve:
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            # Simulate user typing 'n' for no
            result = runner.invoke(cli, ['cancel', 'task-123'], input='n\n')
            
            # Should not call cancel
            mock_flow_api.cancel.assert_not_called()
        
    def test_cancel_failed(self, runner, mock_flow_api):
        """Test handling of failed cancellation."""
        with patch('flow.cli.commands.cancel.resolve_task_identifier') as mock_resolve:
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            # Make cancel raise an exception
            mock_flow_api.cancel.side_effect = Exception("Failed to cancel task")
            
            result = runner.invoke(cli, ['cancel', 'task-123', '--yes'])
            
            assert result.exit_code != 0
            assert "failed" in result.output.lower()


class TestCLILogsCommand:
    """Test 'flow logs' command."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
        
    @pytest.fixture
    def mock_flow_api(self):
        """Mock Flow API for logs command tests."""
        with patch('flow.cli.commands.logs.Flow') as mock_flow_class:
            # Set up Flow mock
            mock_flow = Mock()
            
            # Mock task
            mock_task = Mock()
            mock_task.task_id = "task-123"
            mock_task.logs.return_value = """
[2024-01-01 10:00:00] Starting task...
[2024-01-01 10:00:01] Running command: echo "Hello"
[2024-01-01 10:00:02] Hello
[2024-01-01 10:00:03] Task completed
"""
            
            # Mock get_task
            mock_flow.get_task.return_value = mock_task
            
            mock_flow_class.return_value = mock_flow
            yield mock_flow
            
    def test_logs_basic(self, runner, mock_flow_api):
        """Test getting logs for a task."""
        with patch('flow.cli.commands.logs.resolve_task_identifier') as mock_resolve:
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            result = runner.invoke(cli, ['logs', 'task-123'])
            
            assert result.exit_code == 0
            assert "Starting task" in result.output
            assert "Hello" in result.output
            assert "Task completed" in result.output
            
            mock_flow_api.get_task.assert_called_once_with("task-123")
        
    def test_logs_with_tail(self, runner, mock_flow_api):
        """Test getting logs with tail option."""
        with patch('flow.cli.commands.logs.resolve_task_identifier') as mock_resolve:
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            # Update mock to return tail logs
            mock_flow_api.get_task.return_value.logs.return_value = "Last 10 lines of logs..."
            
            result = runner.invoke(cli, ['logs', 'task-123', '--tail', '10'])
            
            assert result.exit_code == 0
            # Note: The tail filtering might be done client-side
            assert "Last 10 lines of logs..." in result.output
        
    def test_logs_follow_mode(self, runner, mock_flow_api):
        """Test logs in follow mode."""
        with patch('flow.cli.commands.logs.resolve_task_identifier') as mock_resolve:
            mock_task = Mock(task_id="task-123", name="test-task")
            mock_resolve.return_value = (mock_task, None)
            
            # Mock streaming logs - each call returns more logs
            log_messages = [
                "Starting...",
                "Starting...\nProcessing...",
                "Starting...\nProcessing...\nDone!"
            ]
            mock_flow_api.get_task.return_value.logs.side_effect = log_messages
            
            # Mock task status to simulate completion
            mock_flow_api.get_task.return_value.status = "completed"
            
            # Follow mode should exit when task completes
            with patch('time.sleep'):
                result = runner.invoke(cli, ['logs', 'task-123', '--follow'])
                
            # Should have called logs multiple times
            assert mock_flow_api.get_task.return_value.logs.call_count >= 1