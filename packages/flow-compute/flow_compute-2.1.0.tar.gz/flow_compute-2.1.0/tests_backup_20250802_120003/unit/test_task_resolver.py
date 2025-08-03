"""Unit tests for task resolution utilities."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from flow.api.models import Task, TaskStatus
from flow.cli.utils.task_resolver import resolve_task_identifier


def create_mock_task(task_id: str, name: str = None, status: str = "running") -> Task:
    """Create a mock Task object for testing."""
    return Task(
        task_id=task_id,
        name=name or "",  # Task model expects string, not None
        status=TaskStatus(status),
        instance_type="a100",
        created_at=datetime.now(timezone.utc),
        num_instances=1,
        region="us-west-2",
        cost_per_hour="$10.00",
    )


class TestTaskResolver:
    """Test task resolution logic."""
    
    def test_direct_lookup_success(self):
        """Test direct get_task() lookup for exact IDs."""
        expected_task = create_mock_task("task-abc123def", "my-job")
        
        client = Mock()
        client.get_task.return_value = expected_task
        
        task, error = resolve_task_identifier(client, "task-abc123def")
        assert task is not None
        assert error is None
        assert task.task_id == "task-abc123def"
        
        # Should not call list_tasks when direct lookup succeeds
        client.list_tasks.assert_not_called()
    
    def test_direct_lookup_fallback_to_list(self):
        """Test fallback to list when direct lookup fails."""
        tasks = [
            create_mock_task("task-123", "training-job"),
            create_mock_task("task-456", "inference-job"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Task not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "training-job")
        assert task is not None
        assert error is None
        assert task.task_id == "task-123"
        
        # Should have tried direct lookup first
        client.get_task.assert_called_once_with("training-job")
        # Then fallen back to list - fetch_all_tasks calls list_tasks 3 times:
        # 1. For RUNNING status
        # 2. For PENDING status  
        # 3. For general list
        assert client.list_tasks.call_count == 3
    
    def test_exact_id_match(self):
        """Test exact task ID matching takes precedence."""
        tasks = [
            create_mock_task("task-123", "test-123"),
            create_mock_task("task-456", "task-123"),  # name matches our search
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "task-123")
        assert task is not None
        assert error is None
        assert task.task_id == "task-123"
    
    def test_exact_name_match(self):
        """Test exact name matching."""
        tasks = [
            create_mock_task("task-123", "training-job"),
            create_mock_task("task-456", "inference-job"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "training-job")
        assert task is not None
        assert error is None
        assert task.task_id == "task-123"
    
    def test_id_prefix_match(self):
        """Test task ID prefix matching."""
        tasks = [
            create_mock_task("task-abc123def", "job1"),
            create_mock_task("task-xyz789ghi", "job2"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "task-abc")
        assert task is not None
        assert error is None
        assert task.task_id == "task-abc123def"
    
    def test_name_prefix_match(self):
        """Test name prefix matching."""
        tasks = [
            create_mock_task("task-123", "training-large-model"),
            create_mock_task("task-456", "inference-server"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "training")
        assert task is not None
        assert error is None
        assert task.task_id == "task-123"
    
    def test_ambiguous_name_match(self):
        """Test error on ambiguous name matches."""
        tasks = [
            create_mock_task("task-123", "training-v1"),
            create_mock_task("task-456", "training-v2"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "training")
        assert task is None
        assert error is not None
        assert "Multiple tasks match" in error
        assert "training-v1" in error
        assert "training-v2" in error
    
    def test_no_match(self):
        """Test error when no task matches."""
        tasks = [
            create_mock_task("task-123", "job1"),
            create_mock_task("task-456", "job2"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "nonexistent")
        assert task is None
        assert error is not None
        assert "No task found matching 'nonexistent'" in error
        assert "Use 'flow status' to see all tasks" in error
    
    def test_no_match_task_id_format(self):
        """Test enhanced error message for task ID format."""
        tasks = []
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "task-xyz789")
        assert task is None
        assert error is not None
        assert "No task found matching 'task-xyz789'" in error
        assert "Task may still be initializing" in error
        assert "Verify the task ID is correct" in error
        assert "Use 'flow status' to see all tasks" in error
    
    def test_unnamed_task_id_prefix(self):
        """Test matching unnamed tasks by ID prefix."""
        tasks = [
            create_mock_task("task-abc123def", None),
            create_mock_task("task-xyz789ghi", "named-task"),
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "task-abc")
        assert task is not None
        assert error is None
        assert task.task_id == "task-abc123def"
    
    def test_many_ambiguous_matches(self):
        """Test error formatting with many ambiguous matches."""
        tasks = [create_mock_task(f"task-{i}", f"training-job-{i}") for i in range(10)]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        task, error = resolve_task_identifier(client, "training")
        assert task is None
        assert error is not None
        assert "... and 5 more" in error  # Should truncate after 5
    
    def test_exact_match_beats_prefix(self):
        """Test exact matches take precedence over prefix matches."""
        tasks = [
            create_mock_task("task-123", "train"),  # exact name match
            create_mock_task("task-456", "training-job"),  # prefix match
            create_mock_task("train", "other-job"),  # exact ID match wins
        ]
        
        client = Mock()
        client.get_task.side_effect = Exception("Not found")
        client.list_tasks.return_value = tasks
        
        # Exact ID match should win
        task, error = resolve_task_identifier(client, "train")
        assert task is not None
        assert task.task_id == "train"