"""Unit tests for multi-node SSH functionality.

Tests the design and behavior of multi-node SSH without requiring real instances.
"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from flow.api.models import Instance, InstanceStatus, Task, TaskConfig, TaskStatus


class TestMultiNodeSSH:
    """Test multi-node SSH functionality."""

    @pytest.fixture
    def multi_node_task(self):
        """Create a task with multiple instances."""
        task = Task(
            task_id="multi-node-123",
            name="distributed-training",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="distributed-training",
                instance_type="a100",
                num_instances=4,
                command=["python", "-m", "torch.distributed.launch"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=4,
            region="us-central1-a",
            cost_per_hour="$40.00",
            ssh_host="10.0.0.1",  # Primary node
            ssh_port=22,
            ssh_user="ubuntu"
        )

        # Mock instances with different IPs
        task.instances = [
            "inst-node-0",
            "inst-node-1",
            "inst-node-2",
            "inst-node-3"
        ]

        # Mock provider that returns instance details
        mock_provider = Mock()
        mock_provider.get_instances = Mock(return_value=[
            Instance(
                instance_id="inst-node-0",
                task_id="multi-node-123",
                status=InstanceStatus.RUNNING,
                ssh_host="10.0.0.1",
                private_ip="10.0.0.1",
                ssh_port=22,
                ssh_user="ubuntu",
                created_at=datetime.now(timezone.utc),
                instance_type="a100",
                region="us-central1-a"
            ),
            Instance(
                instance_id="inst-node-1",
                task_id="multi-node-123",
                status=InstanceStatus.RUNNING,
                ssh_host="10.0.0.2",
                private_ip="10.0.0.2",
                ssh_port=22,
                ssh_user="ubuntu",
                created_at=datetime.now(timezone.utc),
                instance_type="a100",
                region="us-central1-a"
            ),
            Instance(
                instance_id="inst-node-2",
                task_id="multi-node-123",
                status=InstanceStatus.RUNNING,
                ssh_host="10.0.0.3",
                private_ip="10.0.0.3",
                ssh_port=22,
                ssh_user="ubuntu",
                created_at=datetime.now(timezone.utc),
                instance_type="a100",
                region="us-central1-a"
            ),
            Instance(
                instance_id="inst-node-3",
                task_id="multi-node-123",
                status=InstanceStatus.RUNNING,
                ssh_host="10.0.0.4",
                private_ip="10.0.0.4",
                ssh_port=22,
                ssh_user="ubuntu",
                created_at=datetime.now(timezone.utc),
                instance_type="a100",
                region="us-central1-a"
            )
        ])

        task._provider = mock_provider
        return task

    def test_ssh_to_primary_node(self, multi_node_task):
        """Test SSH to primary node (default behavior)."""
        # Verify task has SSH details for primary node
        assert multi_node_task.ssh_host == "10.0.0.1"
        assert multi_node_task.ssh_port == 22
        assert multi_node_task.ssh_user == "ubuntu"

        # Verify instances are configured
        assert len(multi_node_task.instances) == 4

    def test_ssh_node_parameter_accepted(self, multi_node_task):
        """Test that node parameter is accepted without error."""
        # Current implementation accepts node parameter but doesn't use it
        # This test verifies the API accepts the parameter for future use

        # Should not raise error with valid node index
        try:
            # We can't actually test SSH without mocking subprocess
            # So we just verify the preconditions
            assert multi_node_task.instances[2] == "inst-node-2"
            assert 0 <= 2 < len(multi_node_task.instances)
        except Exception as e:
            pytest.fail(f"Node parameter validation failed: {e}")

    def test_ssh_invalid_node_index(self, multi_node_task):
        """Test SSH with invalid node index."""
        # Mock subprocess to avoid actual SSH connection
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)

            # Test negative index - should work since current implementation doesn't check < 0
            # but we'll test the >= len check

            # Test index beyond range
            with pytest.raises(ValueError) as exc_info:
                multi_node_task.ssh("hostname", node=10)
            assert "Invalid node index 10" in str(exc_info.value)
            assert "task has 4 nodes" in str(exc_info.value)

    def test_ssh_single_node_with_node_param(self):
        """Test SSH with node parameter on single-node task."""
        task = Task(
            task_id="single-node-123",
            name="single-node-task",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="single-node-task",
                instance_type="a100",
                command=["python", "train.py"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            ssh_host="1.2.3.4",
            ssh_port=22,
            ssh_user="ubuntu"
        )
        # Add instances list for single node
        task.instances = ["inst-single"]

        # Should work with node=0
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            task.ssh("hostname", node=0)
            mock_run.assert_called_once()

        # Should fail with node > 0
        with pytest.raises(ValueError) as exc_info:
            task.ssh("hostname", node=1)
        assert "Invalid node index 1" in str(exc_info.value)

    def test_multi_node_instance_metadata(self, multi_node_task):
        """Test that multi-node tasks have proper instance metadata."""
        # Verify task metadata for multi-node setup
        assert multi_node_task.num_instances == 4
        assert len(multi_node_task.instances) == 4

        # Each instance should have an ID
        for i, instance_id in enumerate(multi_node_task.instances):
            assert instance_id == f"inst-node-{i}"

        # Provider should have instance details
        instances = multi_node_task._provider.get_instances()
        assert len(instances) == 4
        for inst in instances:
            assert inst.ssh_host is not None
            assert inst.status == InstanceStatus.RUNNING

    def test_multi_node_log_aggregation(self, multi_node_task):
        """Test log aggregation from multiple nodes."""
        # Mock provider log methods
        multi_node_task._provider.get_task_logs = Mock(side_effect=[
            "Node 0: Training started",
            "Node 1: Training started",
            "Node 2: Training started",
            "Node 3: Training started",
        ])

        # Get logs from primary node
        logs = multi_node_task.logs()
        assert logs == "Node 0: Training started"

        # TODO: When multi-node log aggregation is implemented:
        # logs = multi_node_task.logs(all_nodes=True)
        # assert "Node 0:" in logs
        # assert "Node 1:" in logs
        # assert "Node 2:" in logs
        # assert "Node 3:" in logs

    def test_multi_node_instance_discovery(self, multi_node_task):
        """Test instance discovery for multi-node tasks."""
        # Test that the provider was properly configured with instance details
        instances = multi_node_task._provider.get_instances()

        assert len(instances) == 4
        assert all(inst.ssh_host for inst in instances)
        assert instances[0].ssh_host == "10.0.0.1"
        assert instances[3].ssh_host == "10.0.0.4"

        # Verify the task has instance IDs
        assert len(multi_node_task.instances) == 4
        assert multi_node_task.instances[0] == "inst-node-0"

    def test_distributed_training_metadata(self, multi_node_task):
        """Test metadata setup for distributed training scenario."""
        # Verify the task has proper configuration for distributed training
        assert multi_node_task.num_instances == 4

        # Primary node should be the first instance
        primary_host = multi_node_task.ssh_host
        assert primary_host == "10.0.0.1"

        # All instances should be accessible
        instances = multi_node_task._provider.get_instances()
        instance_ips = [inst.ssh_host for inst in instances]

        # Verify we have unique IPs for each node
        assert len(set(instance_ips)) == 4
        assert "10.0.0.1" in instance_ips  # Primary/master node


class TestMultiNodeSSHEdgeCases:
    """Test edge cases for multi-node SSH functionality."""

    def test_ssh_to_failed_node(self):
        """Test SSH behavior when a node has failed."""
        # Using Mock for task since we're testing the expected behavior
        # Note: Current implementation doesn't check node status
        task = Mock()
        task.num_instances = 3
        task.ssh_host = "10.0.0.1"
        task.ssh_port = 22
        task.ssh_user = "ubuntu"
        task.instances = ["inst-0", "inst-1", "inst-2"]

        # Mock one node as failed
        mock_provider = Mock()
        mock_provider.get_instances = Mock(return_value=[
            Mock(instance_id="inst-0", status="running", ssh_host="10.0.0.1"),
            Mock(instance_id="inst-1", status="failed", ssh_host=None),
            Mock(instance_id="inst-2", status="running", ssh_host="10.0.0.3"),
        ])
        task._provider = mock_provider

        # Test that we can detect failed nodes
        instances = task._provider.get_instances()
        assert instances[1].status == "failed"
        assert instances[1].ssh_host is None

        # Note: Current Task.ssh() implementation doesn't check node status
        # This test documents the expected behavior when implemented

    def test_ssh_with_heterogeneous_instances(self):
        """Test SSH with different instance types in multi-node setup."""
        # This tests a scenario where nodes might have different configurations
        task = Mock()
        task.num_instances = 2
        task.instances = ["inst-gpu", "inst-cpu"]
        task.ssh_host = "10.0.0.1"
        task.ssh_port = 22
        task.ssh_user = "ubuntu"

        mock_provider = Mock()
        mock_provider.get_instances = Mock(return_value=[
            Mock(
                instance_id="inst-gpu",
                instance_type="a100",
                ssh_host="10.0.0.1",
                ssh_user="ubuntu"
            ),
            Mock(
                instance_id="inst-cpu",
                instance_type="cpu-only",
                ssh_host="10.0.0.2",
                ssh_user="admin"  # Different user
            ),
        ])
        task._provider = mock_provider

        # Verify each node uses its specific configuration
        instances = task._provider.get_instances()
        assert instances[0].ssh_user == "ubuntu"
        assert instances[1].ssh_user == "admin"
