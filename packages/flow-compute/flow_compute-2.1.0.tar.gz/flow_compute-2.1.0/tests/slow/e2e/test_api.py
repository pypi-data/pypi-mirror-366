"""Quick API tests - no waiting for instances."""

import time

import pytest

from flow import Flow
from flow.api.models import TaskConfig, TaskStatus


@pytest.mark.e2e
class TestAPI:
    """Test API calls without waiting for instances."""

    @pytest.fixture
    def flow(self):
        # Flow gets API key from environment automatically
        return Flow()

    def test_submit_and_cancel(self, flow):
        """Test task submission API."""
        config = TaskConfig(
            name=f"test-api-{int(time.time())}",
            instance_type="a100",
            command="echo 'API test'",
            max_price_per_hour=100.0,
        )

        task = flow.run(config)
        assert task.task_id.startswith("bid_")

        # Cancel immediately - we're testing API, not provisioning
        flow.cancel(task.task_id)

        # Verify initial status
        assert task.status in [TaskStatus.PENDING, TaskStatus.CANCELLED]

    def test_multi_region_selection(self, flow):
        """Test that multi-region selection works."""
        config = TaskConfig(
            name=f"test-multiregion-{int(time.time())}",
            instance_type="a100",
            command="echo 'Multi-region test'",
            # NO region specified - let provider auto-select
        )

        task = flow.run(config)
        flow.cancel(task.task_id)

        # If we got here without error, multi-region worked
        assert task.task_id

    def test_volume_lifecycle(self, flow):
        """Test volume creation and deletion."""
        # Create
        volume = flow.create_volume(size_gb=1, name=f"test-{int(time.time())}")
        assert volume.volume_id.startswith("vol_")

        # List
        volumes = flow.list_volumes()
        assert any(v.volume_id == volume.volume_id for v in volumes)

        # Delete
        flow.delete_volume(volume.volume_id)

    def test_list_tasks(self, flow):
        """Test task listing."""
        tasks = flow.list_tasks(limit=5)
        assert isinstance(tasks, list)
        assert len(tasks) <= 5
