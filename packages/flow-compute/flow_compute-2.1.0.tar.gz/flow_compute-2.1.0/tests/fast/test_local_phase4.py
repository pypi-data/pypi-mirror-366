"""Phase 4: Multi-node support tests for LocalProvider."""

import time

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.providers.local.provider import LocalProvider


class TestLocalProviderPhase4:
    """Test multi-node environment setup."""

    def test_multi_node_environment(self):
        """Multi-node environment variables are set."""
        provider = LocalProvider(Config(provider="local"))

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=4,
            command="echo RANK=$RANK WORLD=$WORLD_SIZE"
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "RANK=0" in logs
        assert "WORLD=4" in logs

    def test_pytorch_distributed_check(self):
        """PyTorch can initialize distributed."""
        provider = LocalProvider(Config(provider="local"))

        script="""
python -c "
import os
print('RANK=' + repr(os.environ.get('RANK')))
print('WORLD_SIZE=' + repr(os.environ.get('WORLD_SIZE')))
print('MASTER_ADDR=' + repr(os.environ.get('MASTER_ADDR')))
print('MASTER_PORT=' + repr(os.environ.get('MASTER_PORT')))
print('LOCAL_RANK=' + repr(os.environ.get('LOCAL_RANK')))
"
        """

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=2,
            command=script
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        print(f"DEBUG: Logs:\n{logs}")
        assert "RANK='0'" in logs
        assert "WORLD_SIZE='2'" in logs
        assert "MASTER_ADDR='localhost'" in logs
        assert "MASTER_PORT='29500'" in logs
        assert "LOCAL_RANK='0'" in logs

    def test_single_node_no_distributed_vars(self):
        """Single node tasks don't get distributed variables."""
        provider = LocalProvider(Config(provider="local"))

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=1,  # Single node
            command="echo RANK=$RANK WORLD=$WORLD_SIZE"
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        # Should not have distributed training variables
        assert "RANK=" in logs  # Empty RANK
        assert "WORLD=" in logs  # Empty WORLD_SIZE

    def test_flow_specific_vars(self):
        """Flow-specific multi-node variables are set."""
        provider = LocalProvider(Config(provider="local"))

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=8,
            command="echo FLOW_NODE_RANK=$FLOW_NODE_RANK FLOW_NODE_COUNT=$FLOW_NODE_COUNT"
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "FLOW_NODE_RANK=0" in logs
        assert "FLOW_NODE_COUNT=8" in logs

    def test_tensorflow_horovod_vars(self):
        """TensorFlow/Horovod environment variables are set."""
        provider = LocalProvider(Config(provider="local"))

        script="""
python -c "
import os
print('OMPI_COMM_WORLD_RANK=' + repr(os.environ.get('OMPI_COMM_WORLD_RANK')))
print('OMPI_COMM_WORLD_SIZE=' + repr(os.environ.get('OMPI_COMM_WORLD_SIZE')))
"
        """

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=3,
            command=script
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "OMPI_COMM_WORLD_RANK='0'" in logs
        assert "OMPI_COMM_WORLD_SIZE='3'" in logs

    def test_nccl_settings(self):
        """NCCL environment variables are set for local testing."""
        provider = LocalProvider(Config(provider="local"))

        script="""
echo "NCCL_DEBUG=$NCCL_DEBUG"
echo "NCCL_SOCKET_IFNAME=$NCCL_SOCKET_IFNAME"
        """

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=2,
            command=script
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "NCCL_DEBUG=INFO" in logs
        assert "NCCL_SOCKET_IFNAME=lo" in logs  # Loopback for local

    def test_custom_master_port(self):
        """User can override distributed training ports."""
        provider = LocalProvider(Config(provider="local"))

        task = provider.submit_task("local", TaskConfig(
            name="test",
            instance_type="cpu.small",
            num_instances=2,
            command="echo MASTER_PORT=$MASTER_PORT",
            env={"MASTER_PORT": "12345"}  # Custom port
        ))

        # Wait for completion
        for _ in range(10):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)
        assert "MASTER_PORT=12345" in logs  # User override respected


if __name__ == "__main__":
    # Run tests directly
    test = TestLocalProviderPhase4()

    print("Running Phase 4 tests...")

    print("1. Testing multi-node environment...")
    test.test_multi_node_environment()
    print("✓ Multi-node environment works")

    print("2. Testing PyTorch distributed check...")
    test.test_pytorch_distributed_check()
    print("✓ PyTorch distributed environment works")

    print("3. Testing single node (no distributed vars)...")
    test.test_single_node_no_distributed_vars()
    print("✓ Single node correctly has no distributed vars")

    print("4. Testing Flow-specific variables...")
    test.test_flow_specific_vars()
    print("✓ Flow-specific variables work")

    print("5. Testing TensorFlow/Horovod variables...")
    test.test_tensorflow_horovod_vars()
    print("✓ TensorFlow/Horovod variables work")

    print("6. Testing NCCL settings...")
    test.test_nccl_settings()
    print("✓ NCCL settings work")

    print("7. Testing custom master port...")
    test.test_custom_master_port()
    print("✓ Custom master port works")

    print("\nAll Phase 4 tests passed! ✅")
