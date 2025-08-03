"""Simple unit tests for TaskManager that match actual implementation.

These tests focus on the TaskManager's actual behavior and methods.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from flow._internal.managers.task_manager import TaskManager
from flow.api.models import (
    AvailableInstance,
    StorageInterface,
    TaskStatus,
    Volume,
)
from flow.errors import FlowError
from tests.testing import TaskBuilder, TaskConfigBuilder


class TestTaskManagerBasic:
    """Test basic TaskManager functionality."""

    @pytest.fixture
    def mock_compute(self):
        """Create mock compute provider."""
        return Mock()

    @pytest.fixture
    def mock_storage(self):
        """Create mock storage provider."""
        return Mock()

    @pytest.fixture
    def task_manager(self, mock_compute, mock_storage):
        """Create TaskManager with mocks."""
        return TaskManager(
            compute_provider=mock_compute,
            storage_provider=mock_storage
        )

    def test_submit_task_basic_flow(self, task_manager, mock_compute):
        """Test basic task submission flow."""
        # Setup
        mock_compute.find_instances.return_value = [
            AvailableInstance(
                allocation_id="test-alloc",
                instance_type="cpu-small",
                region="us-east-1",
                price_per_hour=1.0
            )
        ]

        mock_compute.submit_task.return_value = (TaskBuilder()
            .with_id("task-001")
            .with_name("test-task")
            .with_status(TaskStatus.PENDING)
            .with_instance_type("cpu-small")
            .build())

        # Test
        config = TaskConfigBuilder().with_cpu("small").build()
        task = task_manager.submit_task(config)

        # Verify
        assert task.task_id == "task-001"
        assert task.status == TaskStatus.PENDING

        # Verify correct calls
        mock_compute.find_instances.assert_called_once()
        mock_compute.submit_task.assert_called_once()

    def test_submit_task_no_instances_available(self, task_manager, mock_compute):
        """Test handling when no instances are available."""
        # No instances available
        mock_compute.find_instances.return_value = []

        config = TaskConfigBuilder().with_gpu("a100-80gb").build()

        # Should raise error
        with pytest.raises(FlowError, match="No instances available"):
            task_manager.submit_task(config)

    def test_get_task_status(self, task_manager, mock_compute):
        """Test getting task status."""
        mock_task = (TaskBuilder()
            .with_id("task-001")
            .with_name("test-task")
            .with_status(TaskStatus.RUNNING)
            .with_instance_type("cpu-small")
            .build())
        mock_compute.get_task.return_value = mock_task

        # Test
        task = task_manager.get_task_status("task-001")

        # Verify
        assert task.task_id == "task-001"
        assert task.status == TaskStatus.RUNNING
        mock_compute.get_task.assert_called_once_with("task-001")

    def test_cancel_task(self, task_manager, mock_compute):
        """Test task cancellation."""
        mock_compute.cancel_task.return_value = True

        # Test
        result = task_manager.cancel_task("task-001")

        # Verify
        assert result is True
        mock_compute.cancel_task.assert_called_once_with("task-001")

    def test_create_volume(self, task_manager, mock_storage):
        """Test volume creation."""
        mock_volume = Volume(
            volume_id="vol-001",
            name="test-volume",
            size_gb=100,
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now()
        )
        mock_storage.create_volume.return_value = mock_volume

        # Test
        volume = task_manager.create_volume(size_gb=100, name="test-volume")

        # Verify
        assert volume.volume_id == "vol-001"
        assert volume.size_gb == 100
        mock_storage.create_volume.assert_called_once()

    def test_submit_task_with_volumes(self, task_manager, mock_compute, mock_storage):
        """Test task submission with volume preparation."""
        # Setup compute
        mock_compute.find_instances.return_value = [
            AvailableInstance(
                allocation_id="test-alloc",
                instance_type="cpu-small",
                region="us-east-1",
                price_per_hour=1.0
            )
        ]

        mock_compute.submit_task.return_value = (TaskBuilder()
            .with_id("task-001")
            .with_name("test-task")
            .with_status(TaskStatus.PENDING)
            .with_instance_type("cpu-small")
            .build())

        # Setup storage
        mock_storage.create_volume.return_value = Volume(
            volume_id="vol-new",
            name="data",
            size_gb=10,
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now()
        )

        # Test with volumes
        config = (TaskConfigBuilder()
            .with_cpu("small")
            .with_volume("/data", size_gb=10)
            .build())

        task = task_manager.submit_task(config)

        # Verify volume was created
        mock_storage.create_volume.assert_called_once()

        # Verify task was submitted with volume IDs
        submit_call = mock_compute.submit_task.call_args
        assert submit_call[1]["volume_ids"] == ["vol-new"]
