"""Fixed CLI status command tests with proper environment isolation.

This module provides properly isolated tests for the status command that
don't pick up real API data from the environment.
"""

import os
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from flow.api.models import Task, TaskStatus
from flow.cli.app import cli


class TestStatusCommandFixed:
    """Fixed status command tests with complete isolation."""
    
    @pytest.fixture
    def isolated_runner(self):
        """Create a Click runner with environment isolation."""
        runner = CliRunner()
        # Use isolated filesystem to prevent config file access
        runner.isolated_filesystem()
        return runner
    
    @pytest.fixture
    def mock_flow_class(self):
        """Mock the Flow class to prevent real API access."""
        with patch('flow.cli.commands.status.Flow') as mock_flow_cls:
            yield mock_flow_cls
    
    @pytest.fixture
    def mock_config(self):
        """Mock Config to prevent environment access."""
        with patch('flow.api.client.Config') as mock_config_cls:
            mock_config = MagicMock()
            mock_config.api_key = "test-api-key"
            mock_config.project = "test-project"
            mock_config.api_url = "http://test-api.local"
            mock_config_cls.from_env.return_value = mock_config
            yield mock_config
    
    def test_status_with_running_task(self, isolated_runner, mock_flow_class, mock_config):
        """Test status command with a running task."""
        # Create mock task
        mock_task = Task(
            task_id="test-123",
            name="test-task",
            status=TaskStatus.RUNNING,
            instance_type="a100",
            num_instances=1,
            region="us-central1-b",
            cost_per_hour="$10.00",
            created_at=datetime.now(timezone.utc),
            started_at=datetime.now(timezone.utc),
        )
        
        # Configure mock Flow instance
        mock_flow = MagicMock()
        mock_flow.list_tasks.return_value = [mock_task]
        mock_flow_class.return_value = mock_flow
        
        # Run command in isolated environment
        with isolated_runner.isolated_filesystem():
            # Clear any Flow environment variables
            env = os.environ.copy()
            for key in list(env.keys()):
                if key.startswith('FLOW_') or key.startswith('FCP_'):
                    del env[key]
            
            # Set test environment
            env['FLOW_API_KEY'] = 'test-key'
            env['FLOW_PROJECT'] = 'test-project'
            
            result = isolated_runner.invoke(
                cli,
                ['status'],
                env=env,
                catch_exceptions=False
            )
        
        assert result.exit_code == 0
        assert "test-task" in result.output
        assert "running" in result.output.lower()
        assert "a100" in result.output.lower() or "A100" in result.output
        
        # Verify mock was called correctly
        mock_flow.list_tasks.assert_called_once()
    
    def test_status_no_tasks(self, isolated_runner, mock_flow_class, mock_config):
        """Test status when no tasks exist."""
        # Configure mock to return empty list
        mock_flow = MagicMock()
        mock_flow.list_tasks.return_value = []
        mock_flow_class.return_value = mock_flow
        
        # Run in complete isolation
        with isolated_runner.isolated_filesystem():
            env = {
                'FLOW_API_KEY': 'test-key',
                'FLOW_PROJECT': 'test-project',
                'HOME': os.getcwd(),  # Prevent access to real home directory
            }
            
            result = isolated_runner.invoke(
                cli,
                ['status'],
                env=env,
                catch_exceptions=False
            )
        
        assert result.exit_code == 0
        assert "no tasks" in result.output.lower() or "no running tasks" in result.output.lower()
        
        mock_flow.list_tasks.assert_called_once()
    
    def test_status_multiple_tasks(self, isolated_runner, mock_flow_class, mock_config):
        """Test status with multiple tasks in different states."""
        # Create multiple mock tasks
        tasks = [
            Task(
                task_id="task-1",
                name="training-job",
                status=TaskStatus.RUNNING,
                instance_type="h100",
                num_instances=1,
                region="us-central1-b",
                cost_per_hour="$25.00",
                created_at=datetime.now(timezone.utc),
                started_at=datetime.now(timezone.utc),
            ),
            Task(
                task_id="task-2",
                name="inference-job",
                status=TaskStatus.COMPLETED,
                instance_type="a100",
                num_instances=1,
                region="us-central1-b",
                cost_per_hour="$10.00",
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            ),
            Task(
                task_id="task-3", 
                name="pending-job",
                status=TaskStatus.PENDING,
                instance_type="t4",
                num_instances=1,
                region="us-central1-b",
                cost_per_hour="$5.00",
                created_at=datetime.now(timezone.utc),
            ),
        ]
        
        mock_flow = MagicMock()
        mock_flow.list_tasks.return_value = tasks
        mock_flow_class.return_value = mock_flow
        
        with isolated_runner.isolated_filesystem():
            result = isolated_runner.invoke(
                cli,
                ['status'],
                env={'FLOW_API_KEY': 'test-key', 'FLOW_PROJECT': 'test-project'},
                catch_exceptions=False
            )
        
        assert result.exit_code == 0
        assert "training-job" in result.output
        assert "inference-job" in result.output
        assert "pending-job" in result.output
        
        # Check status indicators
        assert "running" in result.output.lower()
        assert "completed" in result.output.lower()
        assert "pending" in result.output.lower()
    
    def test_status_with_project_filter(self, isolated_runner, mock_flow_class, mock_config):
        """Test status command with project filter."""
        mock_task = Task(
            task_id="proj-task-1",
            name="project-specific-task",
            status=TaskStatus.RUNNING,
            instance_type="a100",
            num_instances=1,
            region="us-central1-b",
            cost_per_hour="$10.00",
            created_at=datetime.now(timezone.utc),
        )
        
        mock_flow = MagicMock()
        mock_flow.list_tasks.return_value = [mock_task]
        mock_flow.get_current_project.return_value = "specific-project"
        mock_flow_class.return_value = mock_flow
        
        with isolated_runner.isolated_filesystem():
            result = isolated_runner.invoke(
                cli,
                ['status', '--project', 'specific-project'],
                env={'FLOW_API_KEY': 'test-key'},
                catch_exceptions=False
            )
        
        assert result.exit_code == 0
        assert "project-specific-task" in result.output
    
    def test_status_error_handling(self, isolated_runner, mock_flow_class, mock_config):
        """Test status command error handling."""
        # Mock API error
        mock_flow = MagicMock()
        mock_flow.list_tasks.side_effect = Exception("API Error")
        mock_flow_class.return_value = mock_flow
        
        with isolated_runner.isolated_filesystem():
            result = isolated_runner.invoke(
                cli,
                ['status'],
                env={'FLOW_API_KEY': 'test-key'},
                catch_exceptions=True  # Let Click handle the exception
            )
        
        assert result.exit_code != 0
        assert "error" in result.output.lower() or "Error" in result.output


# Standalone test functions that can be used to fix existing tests

def fix_existing_status_test():
    """Example of how to fix an existing status test."""
    from click.testing import CliRunner
    from flow.cli.app import cli
    
    runner = CliRunner()
    
    # Create complete isolation
    with runner.isolated_filesystem():
        with patch('flow.cli.commands.status.Flow') as mock_flow_cls:
            with patch('flow.api.client.Config.from_env') as mock_config:
                # Set up mocks
                mock_config.return_value = MagicMock(
                    api_key="test-key",
                    project="test-project"
                )
                
                mock_flow = MagicMock()
                mock_flow.list_tasks.return_value = []
                mock_flow_cls.return_value = mock_flow
                
                # Run test
                result = runner.invoke(
                    cli,
                    ['status'],
                    env={
                        'FLOW_API_KEY': 'test-key',
                        'HOME': os.getcwd(),  # Isolate home directory
                    }
                )
                
                assert result.exit_code == 0
                assert "no tasks" in result.output.lower()


# Context manager for complete test isolation

from contextlib import contextmanager

@contextmanager
def complete_cli_isolation():
    """Context manager providing complete CLI test isolation."""
    runner = CliRunner()
    
    with runner.isolated_filesystem():
        # Save and clear environment
        original_env = os.environ.copy()
        flow_vars = [k for k in os.environ if k.startswith(('FLOW_', 'FCP_'))]
        for var in flow_vars:
            del os.environ[var]
        
        # Mock all external dependencies
        with patch('flow.cli.commands.status.Flow') as mock_flow_cls:
            with patch('flow.api.client.Config.from_env') as mock_config_fn:
                with patch('flow.api.client.Flow') as mock_flow_api:
                    # Configure default mocks
                    mock_config = MagicMock(
                        api_key="test-key",
                        project="test-project",
                        api_url="http://test.local"
                    )
                    mock_config_fn.return_value = mock_config
                    
                    try:
                        yield {
                            'runner': runner,
                            'mock_flow_cls': mock_flow_cls,
                            'mock_flow_api': mock_flow_api,
                            'mock_config': mock_config,
                        }
                    finally:
                        # Restore environment
                        os.environ.clear()
                        os.environ.update(original_env)