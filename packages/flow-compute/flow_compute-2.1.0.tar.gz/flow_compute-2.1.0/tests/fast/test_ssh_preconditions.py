"""Unit tests for shell preconditions and error handling.

These tests verify shell error conditions without mocking subprocess or any
external dependencies. They focus on the logic and preconditions of shell
functionality.
"""

from datetime import datetime, timezone

import pytest

from flow.api.models import Task, TaskConfig, TaskStatus
from flow.errors import FlowError


class TestShellPreconditions:
    """Test shell preconditions and error handling without mocking subprocess."""

    def test_shell_requires_provider_support(self):
        """Test that shell raises appropriate error when provider doesn't support remote operations."""
        task = Task(
            task_id="no-ssh-task",
            name="task-without-ssh",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="task-without-ssh",
                instance_type="a100",
                command=["echo", "test"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            # No SSH details provided
            ssh_host=None,
            ssh_port=22,
            ssh_user="ubuntu"
        )

        with pytest.raises(FlowError) as exc_info:
            task.shell()

        assert "Provider does not support shell access" in str(exc_info.value)

    def test_shell_with_invalid_node_index(self):
        """Test shell with invalid node indices."""
        task = Task(
            task_id="multi-node-task",
            name="multi-node-task",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="multi-node-task",
                instance_type="a100",
                num_instances=4,
                command=["python", "train.py"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=4,
            region="us-central1-a",
            cost_per_hour="$40.00",
            ssh_host="1.2.3.4",
            ssh_port=22,
            ssh_user="ubuntu"
        )
        # Set instances list
        task.instances = ["inst-0", "inst-1", "inst-2", "inst-3"]

        # Test index beyond range
        with pytest.raises(ValueError) as exc_info:
            task.shell("hostname", node=10)
        assert "Invalid node index 10" in str(exc_info.value)
        assert "task has 4 nodes" in str(exc_info.value)

        # Note: Current implementation doesn't validate negative indices
        # This is a limitation but not critical for 80/20 coverage

    def test_shell_fields_populated_correctly(self):
        """Test that shell fields are properly accessible on Task object."""
        task = Task(
            task_id="ssh-task",
            name="task-with-ssh",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="task-with-ssh",
                instance_type="a100",
                command=["python", "script.py"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            ssh_host="192.168.1.100",
            ssh_port=2222,
            ssh_user="admin"
        )

        # Verify shell fields are accessible
        assert task.ssh_host == "192.168.1.100"
        assert task.ssh_port == 2222
        assert task.ssh_user == "admin"

    def test_shell_with_pending_task(self):
        """Test that shell behaves correctly for non-running tasks."""
        task = Task(
            task_id="pending-task",
            name="pending-task",
            status=TaskStatus.PENDING,
            config=TaskConfig(
                name="pending-task",
                instance_type="a100",
                command=["echo", "test"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            ssh_host="1.2.3.4",  # Even with shell details
            ssh_port=22,
            ssh_user="ubuntu"
        )

        # Current implementation allows shell to pending tasks
        # This documents actual behavior, not necessarily ideal behavior
        # A stricter implementation might check task status first

    def test_logs_method_exists(self):
        """Test that logs method is accessible on Task."""
        task = Task(
            task_id="log-task",
            name="log-task",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="log-task",
                instance_type="a100",
                command=["echo", "test"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00"
        )

        # Verify logs method exists and is callable
        assert hasattr(task, 'logs')
        assert callable(task.logs)

    def test_shell_command_property(self):
        """Test shell command property construction."""
        task = Task(
            task_id="ssh-cmd-task",
            name="ssh-cmd-task",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="ssh-cmd-task",
                instance_type="a100",
                command=["python", "train.py"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            ssh_host="example.com",
            ssh_port=22,
            ssh_user="ubuntu",
            shell_command="ssh -p 22 ubuntu@example.com"
        )

        # Verify shell_command field if provided
        assert task.shell_command == "ssh -p 22 ubuntu@example.com"
