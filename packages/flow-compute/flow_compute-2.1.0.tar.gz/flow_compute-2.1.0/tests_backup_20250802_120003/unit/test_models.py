"""Tests for Flow SDK models."""
from datetime import datetime

import pytest
from pydantic import ValidationError

from flow.api.models import (
    AvailableInstance,
    Instance,
    InstanceStatus,
    ListTasksRequest,
    ListTasksResponse,
    StorageInterface,
    SubmitTaskRequest,
    SubmitTaskResponse,
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
    VolumeSpec,
)


@pytest.mark.unit
@pytest.mark.quick


class TestTaskConfig:
    """Test TaskConfig model."""

    def test_minimal_config(self):
        """Test creating TaskConfig with minimal parameters."""
        config = TaskConfig(
            name="test-task",
            instance_type="a100.80gb.sxm4.1x",
            command="echo test"
        )
        assert config.name == "test-task"
        assert config.instance_type == "a100.80gb.sxm4.1x"
        assert config.image == "nvidia/cuda:12.1.0-runtime-ubuntu22.04"  # default
        assert config.num_instances == 1  # default
        assert config.env == {}
        assert config.volumes == []
        assert config.ssh_keys == []

    def test_full_config(self):
        """Test creating TaskConfig with all parameters."""
        config = TaskConfig(
            name="training-job",
            instance_type="a100.80gb.sxm4.1x",
            num_instances=4,
            region="us-central1-a",
            max_price_per_hour=25.60,
            image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
            command="python train.py --epochs 100",
            env={"MODEL": "gpt-3", "BATCH_SIZE": "128"},
            volumes=[
                VolumeSpec(size_gb=100, mount_path="/data"),
                VolumeSpec(size_gb=50, mount_path="/models", interface=StorageInterface.FILE)
            ],
            ssh_keys=["key-1", "key-2"]
        )
        assert config.name == "training-job"
        assert config.instance_type == "a100.80gb.sxm4.1x"
        assert config.num_instances == 4
        assert config.region == "us-central1-a"
        assert config.max_price_per_hour == 25.60
        assert config.image == "pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime"
        assert config.command == "python train.py --epochs 100"  # String preserved
        # script field was removed from this test
        assert config.env["MODEL"] == "gpt-3"
        # ports field was removed
        assert len(config.volumes) == 2
        assert config.volumes[0].size_gb == 100
        assert config.volumes[1].interface == StorageInterface.FILE
        assert config.ssh_keys == ["key-1", "key-2"]

    def test_gpu_specification_alternatives(self):
        """Test different ways to specify GPU resources."""
        # Using instance type
        config1 = TaskConfig(name="test1", instance_type="a100.80gb.sxm4.1x", command="echo test")
        assert config1.instance_type == "a100.80gb.sxm4.1x"
        assert config1.min_gpu_memory_gb is None

        # Using min_gpu_memory_gb
        config2 = TaskConfig(name="test2", min_gpu_memory_gb=80, command="echo test")
        assert config2.instance_type is None
        assert config2.min_gpu_memory_gb == 80

    def test_invalid_gpu_config(self):
        """Test that mixing instance_type and min_gpu_memory_gb raises error."""
        with pytest.raises(ValidationError):
            TaskConfig(
                name="test",
                instance_type="a100.80gb.sxm4.1x",
                min_gpu_memory_gb=80,
                command="echo test")

    def test_command_normalization(self):
        """Test command field preservation - commands are no longer normalized."""
        # Test string command is preserved as string
        config1 = TaskConfig(
            name="test1",
            instance_type="a100",
            command="python train.py --epochs 100"
        )
        assert config1.command == "python train.py --epochs 100"  # String preserved

        # Test list command is preserved as list
        config2 = TaskConfig(
            name="test2",
            instance_type="a100",
            command=["python", "train.py", "--epochs", "100"]
        )
        assert config2.command == ["python", "train.py", "--epochs", "100"]  # List preserved

        # Test multi-line script is preserved as string
        config3 = TaskConfig(
            name="test3",
            instance_type="a100",
            command="#!/bin/bash\npython train.py --epochs 100"
        )
        assert config3.command == "#!/bin/bash\npython train.py --epochs 100"  # Script preserved

        # Test shell command with pipes is preserved as string
        config4 = TaskConfig(
            name="test4",
            instance_type="a100",
            command="echo 'test' | grep test"
        )
        assert config4.command == "echo 'test' | grep test"  # Shell command preserved
        config5 = TaskConfig(
            name="test5",
            instance_type="a100",
            command="bash -c 'echo hello | grep ello'"
        )
        assert config5.command == "bash -c 'echo hello | grep ello'"  # String preserved

    def test_invalid_command_formats(self):
        """Test that invalid command formats raise errors."""
        # Command accepts string format now, even with unclosed quotes
        config = TaskConfig(
            name="test",
            instance_type="a100",
            command='python -c "unclosed quote'
        )
        assert config.command == 'python -c "unclosed quote'  # String preserved

        # Test invalid type - command must be string or list
        with pytest.raises(ValidationError):
            TaskConfig(
                name="test",
                instance_type="a100",
                command={"not": "valid"}
            )

    def test_incomplete_gpu_config(self):
        """Test that missing GPU config raises error."""
        # Neither instance_type nor min_gpu_memory_gb specified
        with pytest.raises(ValidationError):
            TaskConfig(name="test", command="echo test")

    def test_volume_spec_creation(self):
        """Test VolumeSpec model."""
        volume = VolumeSpec(size_gb=200, mount_path="/data")
        assert volume.size_gb == 200
        assert volume.mount_path == "/data"
        assert volume.interface == StorageInterface.BLOCK  # default
        assert volume.volume_id is None

        # With existing volume
        volume2 = VolumeSpec(size_gb=100, mount_path="/models", volume_id="vol-123")
        assert volume2.volume_id == "vol-123"

    def test_config_name_validation(self):
        """Test name field validation."""
        # Valid name
        config = TaskConfig(name="valid-name_123", instance_type="h100", command="echo test")
        assert config.name == "valid-name_123"

        # Long name is allowed (no max length validation)
        long_name = "a" * 65
        config2 = TaskConfig(name=long_name, instance_type="h100", command="echo test")
        assert config2.name == long_name

        # Empty name should fail pattern validation
        with pytest.raises(ValidationError):
            TaskConfig(name="", instance_type="h100", command="echo test")

        # Invalid characters should fail pattern validation
        with pytest.raises(ValidationError):
            TaskConfig(name="invalid-name!", instance_type="h100", command="echo test")

        # Name starting with hyphen should fail
        with pytest.raises(ValidationError):
            TaskConfig(name="-invalid", instance_type="h100", command="echo test")


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_status_values(self):
        """Test all task status values."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"

    def test_status_membership(self):
        """Test checking if value is valid status."""
        assert "running" in TaskStatus._value2member_map_
        assert "invalid" not in TaskStatus._value2member_map_


class TestTask:
    """Test Task model."""

    def test_task_creation(self):
        """Test creating a Task."""
        task = Task(
            task_id="task-123",
            name="training-job",
            status=TaskStatus.RUNNING,
            created_at=datetime.now(),
            started_at=datetime.now(),
            instance_type="a100.80gb.sxm4.1x",
            num_instances=4,
            region="us-central1-a",
            instances=["i-123", "i-456", "i-789", "i-012"],
            cost_per_hour="$102.40"
        )
        assert task.task_id == "task-123"
        assert task.name == "training-job"
        assert task.status == TaskStatus.RUNNING
        assert task.instance_type == "a100.80gb.sxm4.1x"
        assert task.num_instances == 4
        assert len(task.instances) == 4
        assert task.is_running is True
        assert task.is_terminal is False

    def test_task_terminal_states(self):
        """Test terminal state detection."""
        task_completed = Task(
            task_id="task-1",
            name="job1",
            status=TaskStatus.COMPLETED,
            created_at=datetime.now(),
            instance_type="h100",
            num_instances=1,
            region="us-east-1",
            cost_per_hour="$25.60"
        )
        assert task_completed.is_terminal is True
        assert task_completed.is_running is False

        task_failed = Task(
            task_id="task-2",
            name="job2",
            status=TaskStatus.FAILED,
            created_at=datetime.now(),
            instance_type="h100",
            num_instances=1,
            region="us-east-1",
            cost_per_hour="$25.60"
        )
        assert task_failed.is_terminal is True
        assert task_failed.is_running is False


class TestAvailableInstance:
    """Test AvailableInstance model."""

    def test_available_instance(self):
        """Test creating AvailableInstance."""
        instance = AvailableInstance(
            allocation_id="alloc-123",
            instance_type="a100.80gb.sxm4.1x",
            region="us-central1-a",
            price_per_hour=25.60,
            gpu_count=8,
            cpu_count=64,
            memory_gb=512,
            available_quantity=5,
            status="active",
            expires_at=datetime.now(),
            internode_interconnect="InfiniBand",
            intranode_interconnect="NVLink"
        )
        assert instance.allocation_id == "alloc-123"
        assert instance.instance_type == "a100.80gb.sxm4.1x"
        assert instance.price_per_hour == 25.60
        assert instance.gpu_count == 8
        assert instance.available_quantity == 5


class TestInstance:
    """Test Instance model."""

    def test_instance_creation(self):
        """Test creating an Instance."""
        instance = Instance(
            instance_id="i-1234567890",
            task_id="task-123",
            status=InstanceStatus.RUNNING,
            ssh_host="ubuntu@1.2.3.4",
            private_ip="10.0.0.1",
            created_at=datetime.now()
        )
        assert instance.instance_id == "i-1234567890"
        assert instance.task_id == "task-123"
        assert instance.status == InstanceStatus.RUNNING
        assert instance.ssh_host == "ubuntu@1.2.3.4"
        assert instance.private_ip == "10.0.0.1"
        assert instance.terminated_at is None


class TestVolume:
    """Test Volume model."""

    def test_volume_creation(self):
        """Test creating a Volume."""
        volume = Volume(
            volume_id="vol-123",
            name="training-data",
            size_gb=100,
            region="us-central1-a",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now()
        )
        assert volume.volume_id == "vol-123"
        assert volume.name == "training-data"
        assert volume.size_gb == 100
        assert volume.interface == StorageInterface.BLOCK
        assert volume.attached_to == []

    def test_volume_attachment(self):
        """Test Volume with attachments."""
        volume = Volume(
            volume_id="vol-123",
            name="shared-data",
            size_gb=500,
            region="us-east-1",
            interface=StorageInterface.FILE,
            created_at=datetime.now(),
            attached_to=["i-123", "i-456"]
        )
        assert len(volume.attached_to) == 2
        assert "i-123" in volume.attached_to


class TestRequestResponseModels:
    """Test request/response models."""

    def test_submit_task_request(self):
        """Test SubmitTaskRequest."""
        config = TaskConfig(name="test", instance_type="h100", command="echo test")
        req = SubmitTaskRequest(
            config=config,
            wait=True,
            dry_run=False
        )
        assert req.config.name == "test"
        assert req.wait is True
        assert req.dry_run is False

    def test_submit_task_response(self):
        """Test SubmitTaskResponse."""
        resp = SubmitTaskResponse(
            task_id="task-123",
            status=TaskStatus.PENDING,
            message="Task submitted successfully"
        )
        assert resp.task_id == "task-123"
        assert resp.status == TaskStatus.PENDING
        assert resp.message == "Task submitted successfully"

    def test_list_tasks_request(self):
        """Test ListTasksRequest."""
        req = ListTasksRequest(
            status=TaskStatus.RUNNING,
            limit=50,
            offset=100
        )
        assert req.status == TaskStatus.RUNNING
        assert req.limit == 50
        assert req.offset == 100

    def test_list_tasks_response(self):
        """Test ListTasksResponse."""
        tasks = [
            Task(
                task_id="task-1",
                name="job1",
                status=TaskStatus.RUNNING,
                created_at=datetime.now(),
                instance_type="h100",
                num_instances=1,
                region="us-east-1",
                cost_per_hour="$25.60"
            ),
            Task(
                task_id="task-2",
                name="job2",
                status=TaskStatus.COMPLETED,
                created_at=datetime.now(),
                instance_type="a100",
                num_instances=2,
                region="us-west-2",
                cost_per_hour="$20.48"
            )
        ]
        resp = ListTasksResponse(
            tasks=tasks,
            total=100,
            has_more=True
        )
        assert len(resp.tasks) == 2
        assert resp.total == 100
        assert resp.has_more is True
