"""Test fixtures for Task-related tests."""

from datetime import datetime, timezone
from unittest.mock import Mock

from flow.api.models import Task, TaskStatus


class TaskBuilder:
    """Builder pattern for creating test tasks.
    
    Makes test setup declarative and reusable. Each test should express
    its intent clearly without implementation details.
    """

    def __init__(self):
        self._task_id = "task-test-123"
        self._name = "test-task"
        self._status = TaskStatus.PENDING
        self._instance_type = "a100.80gb.sxm"
        self._region = "us-central1"
        self._created_at = datetime.now(timezone.utc)
        self._cost_per_hour = "$3.60"
        self._ssh_host = None
        self._ssh_user = "ubuntu"

    def with_id(self, task_id: str) -> 'TaskBuilder':
        self._task_id = task_id
        return self

    def with_status(self, status: TaskStatus) -> 'TaskBuilder':
        self._status = status
        return self

    def running(self) -> 'TaskBuilder':
        self._status = TaskStatus.RUNNING
        self._ssh_host = "10.0.0.1"
        return self

    def completed(self) -> 'TaskBuilder':
        self._status = TaskStatus.COMPLETED
        return self

    def with_gpu(self, instance_type: str) -> 'TaskBuilder':
        self._instance_type = instance_type
        return self

    def build(self) -> Task:
        """Build the actual Task object."""
        return Task(
            task_id=self._task_id,
            name=self._name,
            status=self._status,
            instance_type=self._instance_type,
            region=self._region,
            created_at=self._created_at,
            num_instances=1,
            cost_per_hour=self._cost_per_hour,
            ssh_host=self._ssh_host,
            ssh_user=self._ssh_user
        )

    def build_mock(self) -> Mock:
        """Build a Mock that behaves like a Task."""
        task = self.build()
        mock = Mock(spec=Task)

        # Set all attributes
        for attr in ['task_id', 'name', 'status', 'instance_type',
                     'region', 'created_at', 'cost_per_hour', 'ssh_host']:
            setattr(mock, attr, getattr(task, attr))

        return mock


def create_running_task(task_id: str = "task-123") -> Task:
    """Convenience factory for common case."""
    return TaskBuilder().with_id(task_id).running().build()


def create_completed_task(task_id: str = "task-123") -> Task:
    """Convenience factory for completed tasks."""
    return TaskBuilder().with_id(task_id).completed().build()
