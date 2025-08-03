"""Principled unit tests for CLI commands using proper boundary mocking.

Instead of mocking the Flow class (overmocking), we mock at the provider
level which is the actual I/O boundary. This allows us to test the real
CLI command logic while controlling external dependencies.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock

import pytest
import yaml
from click.testing import CliRunner

from flow.api.models import Task, TaskConfig, TaskStatus
from flow.cli.app import cli
from flow.core.provider_interfaces import IProvider
from flow.errors import ResourceNotFoundError, FlowError


class MockProvider(IProvider):
    """Mock provider that implements the IProvider interface."""
    
    def __init__(self):
        self.tasks = {}
        self.next_task_id = 1
        
    def submit_task(self, config: TaskConfig, **kwargs) -> Task:
        """Submit a mock task."""
        task_id = f"task-{self.next_task_id}"
        self.next_task_id += 1
        
        task = Task(
            task_id=task_id,
            name=config.name,
            status=TaskStatus.PENDING,
            instance_type=config.instance_type,
            num_instances=1,
            region="us-central1-b",
            cost_per_hour="$10.00",
            created_at=datetime.now(timezone.utc),
            command=config.command,
        )
        self.tasks[task_id] = task
        return task
        
    def get_task(self, task_id: str) -> Task:
        """Get a task by ID."""
        if task_id not in self.tasks:
            raise ResourceNotFoundError(f"Task {task_id} not found")
        return self.tasks[task_id]
        
    def list_tasks(self, status: Optional[TaskStatus] = None, limit: int = 100) -> List[Task]:
        """List tasks with optional filtering."""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks[:limit]
        
    def cancel_task(self, task_id: str) -> None:
        """Cancel a task."""
        task = self.get_task(task_id)
        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise FlowError(f"Cannot cancel task in {task.status} state")
        task.status = TaskStatus.CANCELLED
        
    def get_logs(self, task_id: str, tail: Optional[int] = None, follow: bool = False) -> str:
        """Get task logs."""
        task = self.get_task(task_id)
        logs = f"[2024-01-01 10:00:00] Starting task {task.name}...\n"
        logs += f"[2024-01-01 10:00:01] Running command: {task.command}\n"
        logs += f"[2024-01-01 10:00:02] Task {task.status.value}\n"
        
        if tail:
            lines = logs.strip().split('\n')
            return '\n'.join(lines[-tail:])
        return logs
        
    def status(self, task_id: str) -> Any:
        """Get task status."""
        task = self.get_task(task_id)
        return Mock(state=task.status.value)


@pytest.fixture
def mock_provider():
    """Create a mock provider instance."""
    return MockProvider()


@pytest.fixture
def mock_flow_with_provider(mock_provider):
    """Patch Flow to use our mock provider."""
    with patch('flow.providers.factory.create_provider') as mock_create:
        mock_create.return_value = mock_provider
        yield mock_provider


class TestCLIStatusCommand:
    """Test status command with proper boundary mocking."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
        
    def test_status_list_tasks(self, runner, mock_flow_with_provider):
        """Test listing tasks."""
        # Add some tasks to the provider
        task1 = Task(
            task_id="task-1",
            name="job-1", 
            status=TaskStatus.RUNNING,
            instance_type="a100",
            num_instances=1,
            region="us-central1-b",
            created_at=datetime.now(timezone.utc),
            cost_per_hour="$10.00"
        )
        task2 = Task(
            task_id="task-2",
            name="job-2",
            status=TaskStatus.COMPLETED,
            instance_type="h100",
            num_instances=1,
            region="us-central1-b",
            cost_per_hour="$25.00",
            created_at=datetime.now(timezone.utc),
            total_cost="$5.00"
        )
        mock_flow_with_provider.tasks = {"task-1": task1, "task-2": task2}
        
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "job-1" in result.output
        assert "job-2" in result.output
        assert "running" in result.output.lower()
        assert "completed" in result.output.lower()
        
    def test_status_no_tasks(self, runner, mock_flow_with_provider):
        """Test status when no tasks exist."""
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert "No tasks found" in result.output


class TestCLICancelCommand:
    """Test cancel command with proper boundary mocking."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
        
    def test_cancel_task(self, runner, mock_flow_with_provider):
        """Test cancelling a task."""
        # Add a running task
        task = Task(
            task_id="task-123",
            name="test-task",
            status=TaskStatus.RUNNING,
            instance_type="a100",
            num_instances=1,
            region="us-central1-b",
            cost_per_hour="$10.00",
            created_at=datetime.now(timezone.utc)
        )
        mock_flow_with_provider.tasks = {"task-123": task}
        
        # Mock task resolution
        with patch('flow.cli.commands.cancel.resolve_task_identifier') as mock_resolve:
            mock_resolve.return_value = (task, None)
            
            result = runner.invoke(cli, ['cancel', 'task-123', '--yes'])
            
            assert result.exit_code == 0
            assert "cancelled" in result.output.lower()
            assert task.status == TaskStatus.CANCELLED


class TestCLILogsCommand:
    """Test logs command with proper boundary mocking."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
        
    def test_logs_basic(self, runner, mock_flow_with_provider):
        """Test getting logs."""
        # Add a task
        task = Task(
            task_id="task-123",
            name="test-task",
            status=TaskStatus.RUNNING,
            instance_type="a100",
            num_instances=1,
            region="us-central1-b",
            cost_per_hour="$10.00",
            created_at=datetime.now(timezone.utc),
            command="echo 'Hello World'"
        )
        mock_flow_with_provider.tasks = {"task-123": task}
        
        # Mock the Flow client's logs method
        with patch('flow.api.client.Flow.logs') as mock_logs:
            mock_logs.return_value = mock_flow_with_provider.get_logs("task-123")
            
            with patch('flow.cli.commands.logs.resolve_task_identifier') as mock_resolve:
                mock_resolve.return_value = (task, None)
                
                result = runner.invoke(cli, ['logs', 'task-123'])
                
                assert result.exit_code == 0
                assert "Starting task test-task" in result.output
                assert "echo 'Hello World'" in result.output


class TestCLIRunCommand:
    """Test run command with proper boundary mocking."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
        
    def test_run_with_config_file(self, runner, mock_flow_with_provider, tmp_path):
        """Test running with config file."""
        # Create config file
        config_file = tmp_path / "job.yaml"
        config_file.write_text("""
name: test-job
instance_type: a100
command: echo "Hello from test"
""")
        
        result = runner.invoke(cli, ['run', str(config_file)])
        
        assert result.exit_code == 0
        assert "task-1" in result.output  # First task ID from mock
        
        # Verify task was created correctly
        created_task = mock_flow_with_provider.tasks.get("task-1")
        assert created_task is not None
        assert created_task.name == "test-job"
        assert created_task.instance_type == "a100"


class TestCLIExampleCommand:
    """Test example command - this one doesn't need provider mocking."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
        
    def test_example_list_all(self, runner):
        """Test listing all examples."""
        result = runner.invoke(cli, ['example'])
        
        assert result.exit_code == 0
        assert "Available examples:" in result.output
        assert "minimal" in result.output
        assert "gpu-test" in result.output
        assert "system-info" in result.output
        assert "training" in result.output
        
    def test_example_show_minimal(self, runner):
        """Test showing minimal example."""
        result = runner.invoke(cli, ['example', 'minimal', '--show'])
        
        assert result.exit_code == 0
        output_yaml = yaml.safe_load(result.output)
        assert output_yaml['name'] == 'minimal-example'
        assert output_yaml['instance_type'] == 'h100-80gb.sxm.8x'
        assert 'Hello from Flow SDK!' in output_yaml['command']