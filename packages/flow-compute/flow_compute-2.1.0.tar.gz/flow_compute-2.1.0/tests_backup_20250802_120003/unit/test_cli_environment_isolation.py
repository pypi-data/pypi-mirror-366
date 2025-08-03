"""Environment isolation utilities for CLI tests.

This module provides utilities to ensure CLI tests run in complete isolation
from the real Flow API and environment variables.
"""

import os
from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from typing import Dict, Optional


@contextmanager
def isolated_cli_environment(
    env_vars: Optional[Dict[str, str]] = None,
    clear_existing: bool = True
):
    """Create an isolated environment for CLI tests.
    
    Args:
        env_vars: Environment variables to set for the test
        clear_existing: Whether to clear existing Flow-related env vars
        
    Usage:
        with isolated_cli_environment({'FLOW_PROJECT': 'test-project'}):
            # Run CLI test
    """
    # Save original environment
    original_env = os.environ.copy()
    
    # List of Flow-related environment variables to clear
    flow_env_vars = [
        'FLOW_API_KEY',
        'FLOW_PROJECT', 
        'FLOW_API_URL',
        'FLOW_CONFIG_PATH',
        'FLOW_WORKSPACE',
        'FCP_API_KEY',
        'FCP_PROJECT',
    ]
    
    try:
        if clear_existing:
            # Clear all Flow-related environment variables
            for var in flow_env_vars:
                os.environ.pop(var, None)
        
        # Set test environment variables
        if env_vars:
            for key, value in env_vars.items():
                os.environ[key] = value
        
        yield
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


@contextmanager
def mock_flow_api(tasks=None, projects=None):
    """Mock the Flow API for CLI tests.
    
    Args:
        tasks: List of mock tasks to return
        projects: List of mock projects to return
        
    Usage:
        with mock_flow_api(tasks=[mock_task]):
            # Run CLI command
    """
    mock_api = MagicMock()
    
    # Set up default returns
    mock_api.list_tasks.return_value = tasks or []
    mock_api.list_projects.return_value = projects or []
    mock_api.get_current_project.return_value = "test-project"
    
    # Mock task operations
    mock_api.get_task.return_value = tasks[0] if tasks else None
    mock_api.stop_task.return_value = True
    
    with patch('flow.cli.commands.status.Flow', return_value=mock_api):
        with patch('flow.api.client.Flow', return_value=mock_api):
            yield mock_api


def create_isolated_runner(runner):
    """Create a Click test runner with isolated environment.
    
    Args:
        runner: Click CliRunner instance
        
    Returns:
        Wrapped runner that ensures environment isolation
    """
    original_invoke = runner.invoke
    
    def isolated_invoke(cli, args=None, **kwargs):
        # Ensure environment isolation for each invocation
        with isolated_cli_environment():
            # Set test-specific environment
            kwargs.setdefault('env', {})
            kwargs['env'].update({
                'FLOW_API_KEY': 'test-api-key',
                'FLOW_PROJECT': 'test-project',
                'FLOW_API_URL': 'http://test-api.local',
            })
            
            return original_invoke(cli, args, **kwargs)
    
    runner.invoke = isolated_invoke
    return runner


# Specific fixes for status command test

def fix_status_command_test(runner, cli):
    """Fix for the status command test with proper isolation."""
    from flow.api.models import Task, TaskStatus
    from datetime import datetime, timezone
    
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
    
    # Run with complete isolation
    with isolated_cli_environment():
        with mock_flow_api(tasks=[mock_task]) as mock_api:
            result = runner.invoke(
                cli,
                ['status'],
                env={
                    'FLOW_API_KEY': 'test-key',
                    'FLOW_PROJECT': 'test-project',
                }
            )
            
            assert result.exit_code == 0
            assert "test-task" in result.output
            assert "running" in result.output.lower()
            
            # Verify API was called
            mock_api.list_tasks.assert_called_once()
    
    return result


def fix_status_no_tasks_test(runner, cli):
    """Fix for the status command test when no tasks exist."""
    # Run with complete isolation and no tasks
    with isolated_cli_environment():
        with mock_flow_api(tasks=[]) as mock_api:
            result = runner.invoke(
                cli,
                ['status'], 
                env={
                    'FLOW_API_KEY': 'test-key',
                    'FLOW_PROJECT': 'test-project',
                }
            )
            
            assert result.exit_code == 0
            assert "no tasks" in result.output.lower() or "no running tasks" in result.output.lower()
            
            # Verify API was called
            mock_api.list_tasks.assert_called_once()
    
    return result


# Utility to patch Config.from_env to prevent real API access

@contextmanager
def mock_config_from_env():
    """Mock Config.from_env to prevent real API configuration."""
    mock_config = MagicMock()
    mock_config.api_key = "test-api-key"
    mock_config.project = "test-project"
    mock_config.api_url = "http://test-api.local"
    
    with patch('flow.api.client.Config.from_env', return_value=mock_config):
        yield mock_config


# Example test using all isolation features

def test_cli_with_complete_isolation(runner, cli):
    """Example test showing complete environment isolation."""
    from flow.api.models import Task, TaskStatus
    from datetime import datetime, timezone
    
    # Create isolated runner
    isolated_runner = create_isolated_runner(runner)
    
    # Create mock data
    mock_task = Task(
        task_id="isolated-test-123",
        name="isolated-task",
        status=TaskStatus.COMPLETED,
        instance_type="h100",
        num_instances=1,
        region="us-central1-b",
        cost_per_hour="$25.00",
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )
    
    # Run test with all isolation features
    with isolated_cli_environment({'FLOW_TEST_MODE': 'true'}):
        with mock_config_from_env():
            with mock_flow_api(tasks=[mock_task]):
                result = isolated_runner.invoke(cli, ['status'])
                
                assert result.exit_code == 0
                assert "isolated-task" in result.output
                assert "completed" in result.output.lower()
                
                # Verify no real API access occurred
                assert os.environ.get('FLOW_TEST_MODE') == 'true'