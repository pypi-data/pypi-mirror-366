"""Test data builders following the Builder pattern.

These builders provide a fluent interface for creating test data with
sensible defaults while allowing customization where needed.
"""

import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Dict, List, Optional

from flow.api.models import (
    AvailableInstance,
    StorageInterface,
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
    VolumeSpec,
)


@dataclass
class TaskConfigBuilder:
    """Immutable builder for TaskConfig test data.
    
    Following the Builder pattern with fluent interface.
    Each method returns a new builder instance (immutability).
    """
    _config: TaskConfig = field(default_factory=lambda: TaskConfig(
        name="test-task",  # Valid default name
        instance_type="a100",  # Default GPU instance type
        command=["echo", "test"],  # Valid default command
        num_instances=1,
        volumes=[],
        env={},
        max_price_per_hour=10.0,
        region=None  # Let provider select region with instances
    ))

    def with_name(self, name: str) -> 'TaskConfigBuilder':
        """Set task name."""
        # Use Pydantic's model_copy for immutable updates
        new_config = self._config.model_copy(update={"name": name})
        return replace(self, _config=new_config)

    def with_instance_type(self, instance_type: str) -> 'TaskConfigBuilder':
        """Set instance type."""
        # Create new config with updated instance_type
        new_config = self._config.model_copy(update={"instance_type": instance_type})
        return replace(self, _config=new_config)

    def with_gpu(self, gpu_type: str = "a100-80gb") -> 'TaskConfigBuilder':
        """Convenience method for GPU configurations."""
        return self.with_instance_type(gpu_type)

    def with_cpu(self, size: str = "small") -> 'TaskConfigBuilder':
        """Convenience method for CPU configurations.
        
        Note: FCP doesn't have CPU-only instances, so this uses a small GPU.
        For integration tests, this will not set instance_type, allowing
        the provider to select any available instance.
        """
        # For integration tests, don't specify instance type
        # Let the provider find any available instance
        return self

    def with_command(self, command: str) -> 'TaskConfigBuilder':
        """Set command to execute."""
        # Convert string to list as expected by TaskConfig
        cmd_list = command.split() if ' ' in command and not any(c in command for c in ['"', "'", '|', '&']) else [command]
        new_config = self._config.model_copy(update={"command": cmd_list})
        return replace(self, _config=new_config)

    def with_script(self, script: str) -> 'TaskConfigBuilder':
        """Set script to execute."""
        new_config = self._config.model_copy(update={"script": script})
        return replace(self, _config=new_config)

    def with_num_instances(self, num: int) -> 'TaskConfigBuilder':
        """Set number of instances."""
        new_config = self._config.model_copy(update={"num_instances": num})
        return replace(self, _config=new_config)

    def with_volumes(self, volumes: List[VolumeSpec]) -> 'TaskConfigBuilder':
        """Set volume specifications."""
        new_config = self._config.model_copy(update={"volumes": volumes})
        return replace(self, _config=new_config)

    def with_volume(self, mount_path: str, size_gb: int = 10) -> 'TaskConfigBuilder':
        """Add a single volume specification."""
        volumes = self._config.volumes.copy() if self._config.volumes else []
        volumes.append(VolumeSpec(mount_path=mount_path, size_gb=size_gb))
        new_config = self._config.model_copy(update={"volumes": volumes})
        return replace(self, _config=new_config)

    def with_environment(self, env: Dict[str, str]) -> 'TaskConfigBuilder':
        """Set environment variables."""
        new_config = self._config.model_copy(update={"env": env})
        return replace(self, _config=new_config)

    def with_env_var(self, key: str, value: str) -> 'TaskConfigBuilder':
        """Add a single environment variable."""
        env_dict = self._config.env.copy() if self._config.env else {}
        env_dict[key] = value
        return self.with_environment(env_dict)

    def with_max_price(self, price: float) -> 'TaskConfigBuilder':
        """Set maximum price per hour."""
        new_config = self._config.model_copy(update={"max_price_per_hour": price})
        return replace(self, _config=new_config)

    def with_region(self, region: str) -> 'TaskConfigBuilder':
        """Set preferred region."""
        new_config = self._config.model_copy(update={"region": region})
        return replace(self, _config=new_config)
    
    def with_upload_code(self, upload: bool) -> 'TaskConfigBuilder':
        """Set whether to upload code."""
        new_config = self._config.model_copy(update={"upload_code": upload})
        return replace(self, _config=new_config)

    def build(self) -> TaskConfig:
        """Build and validate the configuration."""
        config = self._config
        updates = {}

        # Apply sensible defaults if not set
        if not config.name:
            updates["name"] = f"test-task-{uuid.uuid4().hex[:8]}"
        if not config.instance_type:
            # Let tests handle instance type discovery
            pass
        if not config.command and not getattr(config, 'script', None) and not getattr(config, 'shell', None):
            updates["command"] = ["echo", "test"]
        if config.max_price_per_hour is None:
            updates["max_price_per_hour"] = 10.0

        # Apply all updates at once if needed
        if updates:
            config = config.model_copy(update=updates)

        return config


@dataclass
class VolumeBuilder:
    """Builder for Volume test data."""
    _volume_id: str = ""
    _name: str = ""
    _size_gb: int = 10
    _region: str = "us-east-1"
    _interface: StorageInterface = StorageInterface.BLOCK
    _attached_to: List[str] = field(default_factory=list)
    _created_at: Optional[datetime] = None

    def with_id(self, volume_id: str) -> 'VolumeBuilder':
        """Set volume ID."""
        return replace(self, _volume_id=volume_id)

    def with_name(self, name: str) -> 'VolumeBuilder':
        """Set volume name."""
        return replace(self, _name=name)

    def with_size(self, size_gb: int) -> 'VolumeBuilder':
        """Set volume size in GB."""
        return replace(self, _size_gb=size_gb)

    def with_region(self, region: str) -> 'VolumeBuilder':
        """Set volume region."""
        return replace(self, _region=region)

    def with_interface(self, interface: StorageInterface) -> 'VolumeBuilder':
        """Set storage interface type."""
        return replace(self, _interface=interface)

    def attached_to(self, instance_id: str) -> 'VolumeBuilder':
        """Add an attached instance."""
        attached_to = self._attached_to.copy()
        attached_to.append(instance_id)
        return replace(self, _attached_to=attached_to)

    def build(self) -> Volume:
        """Build the Volume object."""
        return Volume(
            volume_id=self._volume_id or f"vol-{uuid.uuid4().hex[:8]}",
            name=self._name or f"test-volume-{uuid.uuid4().hex[:8]}",
            size_gb=self._size_gb,
            region=self._region,
            interface=self._interface,
            attached_to=self._attached_to,
            created_at=self._created_at or datetime.now()
        )


@dataclass
class InstanceBuilder:
    """Builder for AvailableInstance test data."""
    _allocation_id: str = ""
    _instance_type: str = "gpu.nvidia.h100"  # Default instance type for tests
    _region: str = "us-east-1"
    _price_per_hour: float = 1.0
    _gpu_type: Optional[str] = None
    _gpu_count: Optional[int] = None

    def with_id(self, allocation_id: str) -> 'InstanceBuilder':
        """Set allocation ID."""
        return replace(self, _allocation_id=allocation_id)

    def with_type(self, instance_type: str) -> 'InstanceBuilder':
        """Set instance type."""
        return replace(self, _instance_type=instance_type)

    def with_gpu(self, gpu_type: str = "a100-80gb") -> 'InstanceBuilder':
        """Set GPU instance type."""
        return self.with_type(gpu_type)

    def with_region(self, region: str) -> 'InstanceBuilder':
        """Set region."""
        return replace(self, _region=region)

    def with_price(self, price_per_hour: float) -> 'InstanceBuilder':
        """Set price per hour."""
        return replace(self, _price_per_hour=price_per_hour)

    def with_gpu_info(self, gpu_type: str, gpu_count: int) -> 'InstanceBuilder':
        """Set GPU information."""
        return replace(self, _gpu_type=gpu_type, _gpu_count=gpu_count)

    def build(self) -> AvailableInstance:
        """Build the AvailableInstance object."""
        return AvailableInstance(
            allocation_id=self._allocation_id or f"alloc-{uuid.uuid4().hex[:8]}",
            instance_type=self._instance_type,
            region=self._region,
            price_per_hour=self._price_per_hour,
            gpu_type=self._gpu_type,
            gpu_count=self._gpu_count,
        )


@dataclass
class TaskBuilder:
    """Builder for Task test data."""
    _task_id: str = ""
    _name: str = ""
    _status: TaskStatus = TaskStatus.PENDING
    _instance_type: str = "gpu.nvidia.h100"  # Default instance type for tests
    _instance_id: Optional[str] = None  # Will be added to instances list
    _num_instances: int = 1
    _region: str = "us-east-1"
    _cost_per_hour: Optional[str] = None
    _total_cost: Optional[str] = None
    _created_at: Optional[datetime] = None
    _started_at: Optional[datetime] = None
    _completed_at: Optional[datetime] = None

    def with_id(self, task_id: str) -> 'TaskBuilder':
        """Set task ID."""
        return replace(self, _task_id=task_id)

    def with_name(self, name: str) -> 'TaskBuilder':
        """Set task name."""
        return replace(self, _name=name)

    def with_status(self, status: TaskStatus) -> 'TaskBuilder':
        """Set task status."""
        return replace(self, _status=status)

    def with_instance_type(self, instance_type: str) -> 'TaskBuilder':
        """Set instance type."""
        return replace(self, _instance_type=instance_type)

    def with_instance_id(self, instance_id: str) -> 'TaskBuilder':
        """Set instance ID."""
        return replace(self, _instance_id=instance_id)

    def with_cost_per_hour(self, cost: float) -> 'TaskBuilder':
        """Set cost per hour."""
        return replace(self, _cost_per_hour=f"${cost:.2f}")

    def with_total_cost(self, cost: float) -> 'TaskBuilder':
        """Set total cost."""
        return replace(self, _total_cost=f"${cost:.2f}")

    def running(self) -> 'TaskBuilder':
        """Set status to running with started_at."""
        return replace(self,
            _status=TaskStatus.RUNNING,
            _started_at=self._started_at or datetime.now()
        )

    def completed(self, duration_hours: float = 1.0) -> 'TaskBuilder':
        """Set status to completed with times and cost."""
        created_at = self._created_at or datetime.now()
        started_at = self._started_at or created_at
        completed_at = datetime.fromtimestamp(
            started_at.timestamp() + duration_hours * 3600
        )

        # Calculate total cost if cost_per_hour is set
        total_cost = self._total_cost
        if self._cost_per_hour and not total_cost:
            hourly_rate = float(self._cost_per_hour.replace("$", ""))
            total_cost = f"${hourly_rate * duration_hours:.2f}"

        return replace(self,
            _status=TaskStatus.COMPLETED,
            _started_at=started_at,
            _completed_at=completed_at,
            _total_cost=total_cost
        )

    def build(self) -> Task:
        """Build the Task object."""
        task = Task(
            task_id=self._task_id or f"task-{uuid.uuid4().hex[:8]}",
            name=self._name or f"test-task-{uuid.uuid4().hex[:8]}",
            status=self._status,
            instance_type=self._instance_type,
            num_instances=self._num_instances,
            region=self._region,
            cost_per_hour=self._cost_per_hour or "$1.00",  # Default cost
            total_cost=self._total_cost,
            created_at=self._created_at or datetime.now(),
            started_at=self._started_at,
            completed_at=self._completed_at,
        )
        # Add instance_id to instances list if provided
        if self._instance_id:
            task.instances = [self._instance_id]
        return task
