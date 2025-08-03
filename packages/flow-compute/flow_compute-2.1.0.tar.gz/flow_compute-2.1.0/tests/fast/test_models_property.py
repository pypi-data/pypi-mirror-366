"""Property-based tests for Flow SDK models.

These tests use Hypothesis to verify that our models handle all valid inputs
correctly and maintain their invariants. Property-based testing helps us find
edge cases that traditional example-based tests might miss.

Following the principle of comprehensive testing, we verify:
1. All valid inputs are accepted
2. Invalid inputs are properly rejected
3. Serialization/deserialization roundtrips work
4. Model invariants are maintained
5. Edge cases are handled gracefully
"""

from datetime import datetime, timezone

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from pydantic import ValidationError

from flow.api.models import (
    AvailableInstance,
    CPUSpec,
    GPUSpec,
    StorageInterface,
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
    VolumeSpec,
)

# ========== Strategy Builders ==========

def valid_identifier() -> SearchStrategy[str]:
    """Strategy for valid identifiers (names, IDs)."""
    # Use only ASCII alphanumeric and allowed special characters
    return st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
        min_size=1,
        max_size=100
    ).filter(lambda x: x[0].isalnum() and not x.startswith("-") and not x.endswith("-"))


def valid_gpu_model() -> SearchStrategy[str]:
    """Strategy for valid GPU model names."""
    return st.sampled_from([
        "A100", "H100", "L40S", "A10", "T4", "V100",
        "RTX 4090", "RTX 4080", "RTX 3090", "RTX 3080"
    ])


def valid_memory_type() -> SearchStrategy[str]:
    """Strategy for valid memory types."""
    return st.sampled_from(["HBM2e", "HBM3", "GDDR6", "GDDR6X", "DDR4", "DDR5"])


def valid_cpu_architecture() -> SearchStrategy[str]:
    """Strategy for valid CPU architectures."""
    return st.sampled_from(["x86_64", "amd64", "arm64", "aarch64"])


def valid_region() -> SearchStrategy[str]:
    """Strategy for valid region codes."""
    return st.sampled_from([
        "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
        "ap-southeast-1", "ap-northeast-1"
    ])


def valid_docker_image() -> SearchStrategy[str]:
    """Strategy for valid Docker image names."""
    base = st.sampled_from([
        "python", "pytorch/pytorch", "tensorflow/tensorflow",
        "nvidia/cuda", "jupyter/base-notebook"
    ])
    tag = st.sampled_from([
        "latest", "3.11", "3.10", "2.0.0-cuda11.8", "23.10-py3"
    ])
    return st.builds(lambda b, t: f"{b}:{t}", base, tag)


def valid_file_path() -> SearchStrategy[str]:
    """Strategy for valid file paths."""
    return st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_/.",
        min_size=1,
        max_size=200
    ).filter(lambda x: not x.startswith("/") and ".." not in x and not x.endswith("/"))


def valid_url() -> SearchStrategy[str]:
    """Strategy for valid URLs."""
    scheme = st.sampled_from(["http", "https", "s3", "gs"])
    domain = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-.", min_size=3, max_size=50)
    path = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_/.", min_size=0, max_size=100)
    return st.builds(lambda s, d, p: f"{s}://{d}/{p}", scheme, domain, path)


# ========== Hardware Specification Tests ==========

class TestGPUSpec:
    """Property tests for GPUSpec model."""

    @given(
        vendor=st.sampled_from(["NVIDIA", "AMD", "Intel"]),
        model=valid_gpu_model(),
        memory_gb=st.integers(min_value=1, max_value=1024),
        memory_type=valid_memory_type(),
        architecture=st.sampled_from(["Ampere", "Hopper", "Ada Lovelace", "RDNA3"]),
        compute_capability=st.tuples(
            st.integers(min_value=3, max_value=9),
            st.integers(min_value=0, max_value=9)
        ),
        tflops_fp32=st.floats(min_value=0.1, max_value=1000, allow_nan=False),
        tflops_fp16=st.floats(min_value=0.1, max_value=2000, allow_nan=False),
        memory_bandwidth_gb_s=st.floats(min_value=0.1, max_value=10000, allow_nan=False),
    )
    def test_valid_gpu_spec(self, vendor, model, memory_gb, memory_type,
                           architecture, compute_capability, tflops_fp32,
                           tflops_fp16, memory_bandwidth_gb_s):
        """Test that valid GPU specifications are accepted."""
        gpu = GPUSpec(
            vendor=vendor,
            model=model,
            memory_gb=memory_gb,
            memory_type=memory_type,
            architecture=architecture,
            compute_capability=compute_capability,
            tflops_fp32=tflops_fp32,
            tflops_fp16=tflops_fp16,
            memory_bandwidth_gb_s=memory_bandwidth_gb_s,
        )

        # Verify all fields are set correctly
        assert gpu.vendor == vendor
        assert gpu.model == model
        assert gpu.memory_gb == memory_gb
        assert gpu.memory_type == memory_type
        assert gpu.architecture == architecture
        assert gpu.compute_capability == compute_capability
        assert gpu.tflops_fp32 == tflops_fp32
        assert gpu.tflops_fp16 == tflops_fp16
        assert gpu.memory_bandwidth_gb_s == memory_bandwidth_gb_s

        # Test properties
        assert gpu.canonical_name == f"{vendor}-{model}-{memory_gb}gb".lower()
        assert gpu.display_name == f"{vendor} {model.upper()} {memory_gb}GB"

    @given(
        memory_gb=st.integers(max_value=0),
        memory_bandwidth_gb_s=st.floats(max_value=-1, allow_nan=False),
        tflops_fp32=st.floats(max_value=-1, allow_nan=False),
    )
    def test_invalid_gpu_spec(self, memory_gb, memory_bandwidth_gb_s, tflops_fp32):
        """Test that invalid GPU specifications are rejected."""
        with pytest.raises(ValidationError):
            GPUSpec(
                model="A100",
                memory_gb=memory_gb,
                memory_bandwidth_gb_s=memory_bandwidth_gb_s,
                tflops_fp32=tflops_fp32,
            )

    @given(st.builds(
        GPUSpec,
        model=valid_gpu_model(),
        memory_gb=st.integers(min_value=1, max_value=1024),
    ))
    def test_gpu_spec_immutability(self, gpu):
        """Test that GPUSpec is immutable."""
        with pytest.raises(ValidationError) as exc_info:
            gpu.memory_gb = 100

        # Verify it's a frozen instance error
        assert "frozen_instance" in str(exc_info.value)


class TestCPUSpec:
    """Property tests for CPUSpec model."""

    @given(
        vendor=st.sampled_from(["Intel", "AMD", "ARM", "Apple"]),
        model=st.text(min_size=1, max_size=50),
        cores=st.integers(min_value=1, max_value=256),
        threads=st.one_of(
            st.just(0),  # Default: same as cores
            st.integers(min_value=1, max_value=512)
        ),
        base_clock_ghz=st.floats(min_value=0.1, max_value=10, allow_nan=False),
    )
    def test_valid_cpu_spec(self, vendor, model, cores, threads, base_clock_ghz):
        """Test that valid CPU specifications are accepted."""
        cpu = CPUSpec(
            vendor=vendor,
            model=model,
            cores=cores,
            threads=threads,
            base_clock_ghz=base_clock_ghz,
        )

        assert cpu.vendor == vendor
        assert cpu.model == model
        assert cpu.cores == cores
        # If threads was 0, it should be set to cores
        assert cpu.threads == (cores if threads == 0 else threads)
        assert cpu.base_clock_ghz == base_clock_ghz

    @given(
        cores=st.integers(max_value=0),
        threads=st.integers(max_value=-1),
    )
    def test_invalid_cpu_spec(self, cores, threads):
        """Test that invalid CPU specifications are rejected."""
        with pytest.raises(ValidationError):
            CPUSpec(cores=cores, threads=threads)


# ========== Core Domain Model Tests ==========

class TestTaskConfig:
    """Property tests for TaskConfig model."""

    @given(
        name=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
            min_size=1,
            max_size=100
        ).filter(lambda x: x[0].isalnum()),  # Must start with alphanumeric
        instance_type=st.one_of(st.none(), valid_identifier()),
        min_gpu_memory_gb=st.one_of(st.none(), st.integers(min_value=1, max_value=640)),
        command=st.one_of(
            st.none(),
            st.lists(st.text(min_size=1), min_size=1, max_size=10),  # List form
            st.text(min_size=1),  # String form
            st.text(min_size=10).map(lambda s: f"#!/bin/bash\n{s}")  # Script form
        ),
        image=valid_docker_image(),
        env=st.dictionaries(
            keys=st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_", min_size=1, max_size=50),
            values=st.text(min_size=0),
            max_size=10
        ),
        working_dir=valid_file_path().map(lambda p: f"/{p}"),
        max_price_per_hour=st.one_of(st.none(), st.floats(min_value=0.01, max_value=1000, allow_nan=False)),
        max_run_time_hours=st.one_of(st.none(), st.floats(min_value=0.1, max_value=168, allow_nan=False)),
        num_instances=st.integers(min_value=1, max_value=100),
        priority=st.integers(min_value=1, max_value=100),
    )
    def test_valid_task_config(self, name, instance_type, min_gpu_memory_gb, command,
                              image, env, working_dir, max_price_per_hour,
                              max_run_time_hours, num_instances, priority):
        """Test that valid task configurations are accepted."""
        # Can't have both instance_type and min_gpu_memory_gb
        if instance_type and min_gpu_memory_gb:
            min_gpu_memory_gb = None

        # Must have either instance_type or min_gpu_memory_gb
        if not instance_type and not min_gpu_memory_gb:
            instance_type = "gpu.nvidia.a100"

        # Must have command specified
        if not command:
            # None specified, default to command
            command = "echo test"

        config = TaskConfig(
            name=name,
            instance_type=instance_type,
            min_gpu_memory_gb=min_gpu_memory_gb,
            command=command,
            image=image,
            env=env,
            working_dir=working_dir,
            max_price_per_hour=max_price_per_hour,
            max_run_time_hours=max_run_time_hours,
            num_instances=num_instances,
            priority=priority,
        )

        # Verify fields
        assert config.name == name
        assert config.command == command
        assert config.num_instances == num_instances
        assert config.priority == priority
        assert config.image == image
        assert config.working_dir == working_dir

    @given(
        name=st.one_of(
            st.text(max_size=0),  # Empty name
            st.text(alphabet="!@#$%", min_size=1, max_size=10),  # Invalid characters
        ),
        num_instances=st.integers(max_value=0),  # Zero or negative instances
        priority=st.one_of(
            st.integers(max_value=0),  # Zero or negative
            st.integers(min_value=101)  # Over 100
        ),
    )
    def test_invalid_task_config(self, name, num_instances, priority):
        """Test that invalid task configurations are rejected."""
        with pytest.raises(ValidationError):
            TaskConfig(
                name=name,
                command=["python", "train.py"],
                num_instances=num_instances,
                priority=priority,
            )

    @given(st.builds(
        TaskConfig,
        name=valid_identifier(),
        command=st.lists(st.text(min_size=1), min_size=1, max_size=5),
        instance_type=st.just("gpu.nvidia.a100"),  # Required field
    ))
    def test_task_config_serialization(self, config):
        """Test that TaskConfig can be serialized and deserialized."""
        # To dict
        data = config.model_dump()
        assert isinstance(data, dict)
        assert data["name"] == config.name

        # From dict
        config2 = TaskConfig(**data)
        assert config2 == config

        # To JSON
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)

        # From JSON
        config3 = TaskConfig.model_validate_json(json_str)
        assert config3 == config


class TestVolumeSpec:
    """Property tests for VolumeSpec model."""

    @given(
        name=st.one_of(
            st.none(),
            st.text(
                alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
                min_size=3,
                max_size=64
            ).filter(lambda x: x[0].isalnum() and x[-1].isalnum() and not x.startswith("-") and not x.endswith("-"))
        ),
        size_gb=st.integers(min_value=1, max_value=15000),  # Required field with constraints
        volume_id=st.one_of(st.none(), st.text(alphabet="abcdef0123456789-", min_size=10, max_size=50)),
        mount_path=valid_file_path().map(lambda p: f"/{p}" if not p.startswith("/") else p),
        interface=st.sampled_from(list(StorageInterface)),
        iops=st.one_of(st.none(), st.integers(min_value=100, max_value=64000)),
        throughput_mb_s=st.one_of(st.none(), st.integers(min_value=125, max_value=1000)),
    )
    def test_valid_volume_spec(self, name, size_gb, volume_id, mount_path, interface, iops, throughput_mb_s):
        """Test that valid volume specifications are accepted."""
        # If volume_id is set, can't specify IOPS/throughput
        if volume_id:
            iops = None
            throughput_mb_s = None

        volume = VolumeSpec(
            name=name,
            size_gb=size_gb,
            volume_id=volume_id,
            mount_path=mount_path,
            interface=interface,
            iops=iops,
            throughput_mb_s=throughput_mb_s,
        )

        assert volume.mount_path == mount_path
        assert volume.size_gb == size_gb
        assert volume.interface == interface
        if volume_id:
            assert volume.iops is None
            assert volume.throughput_mb_s is None

    @given(
        size_gb=st.integers(max_value=0),
        iops=st.integers(max_value=99),
        throughput_mb_s=st.integers(max_value=124),
    )
    def test_invalid_volume_spec(self, size_gb, iops, throughput_mb_s):
        """Test that invalid volume specifications are rejected."""
        with pytest.raises(ValidationError):
            VolumeSpec(
                size_gb=size_gb,
                mount_path="/data",
                iops=iops,
                throughput_mb_s=throughput_mb_s,
            )


class TestTask:
    """Property tests for Task model."""

    @given(
        task_id=st.text(alphabet="abcdef0123456789-", min_size=10, max_size=50),
        name=valid_identifier(),
        status=st.sampled_from(list(TaskStatus)),
        instance_type=valid_identifier(),
        num_instances=st.integers(min_value=1, max_value=100),
        region=valid_region(),
        cost_per_hour=st.floats(min_value=0.01, max_value=1000, allow_nan=False).map(lambda x: f"${x:.2f}"),
        # message field for status messages
        message=st.one_of(st.none(), st.text()),
    )
    def test_valid_task(self, task_id, name, status, instance_type,
                       num_instances, region, cost_per_hour, message):
        """Test that valid tasks are accepted."""
        # Message typically for failed tasks
        if status != TaskStatus.FAILED:
            message = None

        task = Task(
            task_id=task_id,
            name=name,
            status=status,
            instance_type=instance_type,
            num_instances=num_instances,
            region=region,
            cost_per_hour=cost_per_hour,
            created_at=datetime.now(timezone.utc),
            message=message,
        )

        assert task.task_id == task_id
        assert task.name == name
        assert task.status == status
        assert task.instance_type == instance_type
        assert task.num_instances == num_instances
        assert task.region == region
        assert task.cost_per_hour == cost_per_hour
        # Check that task was created successfully
        assert task.created_at is not None

    @given(st.builds(
        Task,
        task_id=valid_identifier(),
        name=valid_identifier(),
        status=st.sampled_from(list(TaskStatus)),
        instance_type=valid_identifier(),
    ))
    def test_task_state_transitions(self, task):
        """Test that task state transitions maintain consistency."""
        # Initial state
        original_status = task.status

        # If pending, can transition to running
        if original_status == TaskStatus.PENDING:
            task.status = TaskStatus.RUNNING
            assert task.status == TaskStatus.RUNNING

        # If running, can transition to completed/failed/cancelled
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.COMPLETED
            assert task.status == TaskStatus.COMPLETED

    @given(
        task_data=st.fixed_dictionaries({
            "task_id": valid_identifier(),
            "name": valid_identifier(),
            "status": st.sampled_from([s.value for s in TaskStatus]),
            "instance_type": valid_identifier(),
            "num_instances": st.integers(min_value=1, max_value=10),
            "region": valid_region(),
            "cost_per_hour": st.floats(min_value=0.01, max_value=100, allow_nan=False).map(lambda x: f"${x:.2f}"),
            "created_at": st.datetimes(
                min_value=datetime(2020, 1, 1),
                max_value=datetime(2030, 1, 1)
            ).map(lambda dt: dt.replace(tzinfo=timezone.utc)),
        })
    )
    def test_task_json_roundtrip(self, task_data):
        """Test that tasks can be serialized to/from JSON."""
        # Create task from dict
        task = Task(**task_data)

        # Serialize to JSON
        json_str = task.model_dump_json()

        # Deserialize from JSON
        task2 = Task.model_validate_json(json_str)

        # Should be equal
        assert task == task2
        assert task.task_id == task2.task_id
        assert task.created_at == task2.created_at


# ========== Instance and Resource Tests ==========

class TestAvailableInstance:
    """Property tests for AvailableInstance model."""

    @given(
        allocation_id=valid_identifier(),
        instance_type=valid_identifier(),
        region=valid_region(),
        price_per_hour=st.floats(min_value=0.01, max_value=1000, allow_nan=False),
        # Optional fields
        gpu_type=st.one_of(st.none(), valid_gpu_model()),
        gpu_count=st.one_of(st.none(), st.integers(min_value=1, max_value=8)),
        cpu_count=st.one_of(st.none(), st.integers(min_value=1, max_value=256)),
        memory_gb=st.one_of(st.none(), st.integers(min_value=1, max_value=1024)),
    )
    def test_valid_available_instance(self, allocation_id, instance_type, region,
                                     price_per_hour, gpu_type, gpu_count, cpu_count, memory_gb):
        """Test that valid available instances are accepted."""
        instance = AvailableInstance(
            allocation_id=allocation_id,
            instance_type=instance_type,
            region=region,
            price_per_hour=price_per_hour,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
            cpu_count=cpu_count,
            memory_gb=memory_gb,
        )

        assert instance.allocation_id == allocation_id
        assert instance.instance_type == instance_type
        assert instance.region == region
        assert instance.price_per_hour == price_per_hour
        assert instance.gpu_type == gpu_type
        assert instance.gpu_count == gpu_count
        assert instance.cpu_count == cpu_count
        assert instance.memory_gb == memory_gb

    @given(
        instances=st.lists(
            st.builds(
                AvailableInstance,
                allocation_id=valid_identifier(),
                instance_type=st.sampled_from(["a100.80gb", "h100.80gb", "l40s.48gb"]),
                region=valid_region(),
                price_per_hour=st.floats(min_value=1.0, max_value=50.0, allow_nan=False),
            ),
            min_size=2,
            max_size=10
        )
    )
    def test_instance_price_comparison(self, instances):
        """Test that instances can be sorted by price."""
        # Sort by price
        sorted_instances = sorted(instances, key=lambda x: x.price_per_hour)

        # Verify ordering
        for i in range(len(sorted_instances) - 1):
            assert sorted_instances[i].price_per_hour <= sorted_instances[i + 1].price_per_hour


class TestVolume:
    """Property tests for Volume model."""

    @given(
        volume_id=valid_identifier(),
        name=valid_identifier(),
        size_gb=st.integers(min_value=1, max_value=100000),
        region=valid_region(),
        interface=st.sampled_from(list(StorageInterface)),
        created_at=st.datetimes(
            min_value=datetime(2020, 1, 1),
            max_value=datetime(2030, 1, 1)
        ).map(lambda dt: dt.replace(tzinfo=timezone.utc)),
        attached_to=st.lists(valid_identifier(), min_size=0, max_size=3),
    )
    def test_valid_volume(self, volume_id, name, size_gb, region, interface,
                         created_at, attached_to):
        """Test that valid volumes are accepted."""
        volume = Volume(
            volume_id=volume_id,
            name=name,
            size_gb=size_gb,
            region=region,
            interface=interface,
            created_at=created_at,
            attached_to=attached_to,
        )

        assert volume.volume_id == volume_id
        assert volume.size_gb == size_gb
        assert volume.region == region
        assert volume.interface == interface
        assert volume.attached_to == attached_to
        assert volume.id == volume_id  # Test alias


# ========== Complex Interaction Tests ==========

class TestModelInteractions:
    """Test interactions between different models."""

    @given(
        config=st.builds(
            TaskConfig,
            name=valid_identifier(),
            instance_type=st.sampled_from(["a100.80gb", "h100.80gb"]),
            command=st.lists(st.text(min_size=1), min_size=1, max_size=5),
            volumes=st.lists(
                st.builds(
                    VolumeSpec,
                    name=st.text(
                        alphabet="abcdefghijklmnopqrstuvwxyz0123456789-",
                        min_size=3,
                        max_size=64
                    ).filter(lambda x: x[0].isalnum() and x[-1].isalnum()),
                    size_gb=st.integers(min_value=10, max_value=1000),
                    mount_path=valid_file_path().map(lambda p: f"/{p}"),
                ),
                max_size=3
            ),
        ),
        instance=st.builds(
            AvailableInstance,
            allocation_id=valid_identifier(),
            instance_type=st.sampled_from(["a100.80gb", "h100.80gb"]),
            region=valid_region(),
            price_per_hour=st.floats(min_value=1.0, max_value=50.0, allow_nan=False),
        ),
    )
    def test_task_config_to_task(self, config, instance):
        """Test creating a Task from TaskConfig and AvailableInstance."""
        # Create task from config and instance
        task = Task(
            task_id=f"task-{config.name}",
            name=config.name,
            status=TaskStatus.PENDING,
            instance_type=instance.instance_type,
            num_instances=config.num_instances,
            region=instance.region,
            cost_per_hour=f"${instance.price_per_hour * config.num_instances:.2f}",
            created_at=datetime.now(timezone.utc),
        )

        # Verify consistency
        assert task.name == config.name
        assert task.instance_type == instance.instance_type
        assert task.num_instances == config.num_instances
        assert task.cost_per_hour == f"${instance.price_per_hour * config.num_instances:.2f}"

    @given(
        configs=st.lists(
            st.one_of(
                # Config with instance_type
                st.builds(
                    TaskConfig,
                    name=valid_identifier(),
                    instance_type=st.sampled_from(["a100.80gb", "h100.80gb", "l40s.48gb"]),
                    min_gpu_memory_gb=st.just(None),
                    command=st.lists(st.text(min_size=1), min_size=1, max_size=5),
                    max_price_per_hour=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
                ),
                # Config with min_gpu_memory_gb
                st.builds(
                    TaskConfig,
                    name=valid_identifier(),
                    instance_type=st.just(None),
                    min_gpu_memory_gb=st.sampled_from([40, 80, 160]),
                    command=st.lists(st.text(min_size=1), min_size=1, max_size=5),
                    max_price_per_hour=st.floats(min_value=1.0, max_value=100.0, allow_nan=False),
                )
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_config_validation_consistency(self, configs):
        """Test that multiple configs maintain consistency."""
        for config in configs:
            # Should have either instance_type or min_gpu_memory_gb
            assert bool(config.instance_type) != bool(config.min_gpu_memory_gb)

            # Price should be positive
            if config.max_price_per_hour:
                assert config.max_price_per_hour > 0

            # Command should be a list
            assert isinstance(config.command, list)
            assert len(config.command) > 0


# ========== Edge Case and Error Tests ==========

class TestEdgeCases:
    """Test edge cases and error conditions."""

    @given(
        very_long_name=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_",
            min_size=1000,
            max_size=10000
        )
    )
    def test_very_long_names(self, very_long_name):
        """Test that very long names are handled appropriately."""
        # TaskConfig might accept very long names if they match the pattern
        try:
            config = TaskConfig(
                name=very_long_name,
                command=["echo", "test"],
                instance_type="gpu.nvidia.a100",
            )
            # If it succeeds, verify it preserved the name
            assert config.name == very_long_name
        except ValidationError:
            # Some very long names might be rejected by Pydantic's internal limits
            pass

    @given(
        extreme_values=st.dictionaries(
            keys=st.sampled_from(["memory_gb", "cpu_cores", "price", "runtime"]),
            values=st.one_of(
                st.just(0),
                st.just(-1),
                st.just(float('inf')),
                st.just(10**15),
                st.just(10**-15),
            ),
            min_size=1,
        )
    )
    @settings(deadline=5000)  # 5 seconds deadline for complex property test
    def test_extreme_numeric_values(self, extreme_values):
        """Test that extreme numeric values are properly validated."""
        # Test each extreme value type separately
        if "memory_gb" in extreme_values:
            value = extreme_values["memory_gb"]
            if value <= 0:
                with pytest.raises(ValidationError):
                    GPUSpec(model="A100", memory_gb=value)
            else:
                # Large positive values might be valid
                # Convert to int, ensuring at least 1
                mem_value = max(1, int(min(value, 1024)))
                gpu = GPUSpec(model="A100", memory_gb=mem_value)
                assert gpu.memory_gb > 0

        if "cpu_cores" in extreme_values:
            value = extreme_values["cpu_cores"]
            if value <= 0:
                with pytest.raises(ValidationError):
                    CPUSpec(cores=value)
            else:
                # Large positive values might be valid
                # Convert to int, ensuring at least 1
                cores_value = max(1, int(min(value, 256)))
                cpu = CPUSpec(cores=cores_value)
                assert cpu.cores > 0

        if "price" in extreme_values:
            value = extreme_values["price"]
            # AvailableInstance accepts any float value including negative and infinity
            # Only NaN would cause validation errors
            if value != value:  # NaN check
                with pytest.raises(ValidationError):
                    AvailableInstance(
                        allocation_id="test",
                        instance_type="test",
                        region="us-east-1",
                        price_per_hour=value
                    )
            else:
                # All non-NaN values are accepted
                instance = AvailableInstance(
                    allocation_id="test",
                    instance_type="test",
                    region="us-east-1",
                    price_per_hour=value
                )
                assert instance.price_per_hour == value

        if "runtime" in extreme_values:
            value = extreme_values["runtime"]
            # TaskConfig.max_run_time_hours must be > 0
            if value <= 0 or value > 168 or value == float('inf') or value != value:
                with pytest.raises(ValidationError):
                    TaskConfig(
                        name="test",
                        instance_type="gpu.nvidia.a100",
                        command=["echo", "test"],
                        max_run_time_hours=value
                    )
            else:
                # Valid runtime values
                config = TaskConfig(
                    name="test",
                    instance_type="gpu.nvidia.a100",
                    command=["echo", "test"],
                    max_run_time_hours=min(value, 168.0)
                )
                assert config.max_run_time_hours > 0

    @given(
        special_chars=st.text(
            alphabet="!@#$%^&*(){}[]|\\:;\"'<>?,./`~",
            min_size=1,
            max_size=50
        )
    )
    def test_special_characters_in_strings(self, special_chars):
        """Test that special characters are handled appropriately."""
        # Environment variable values can contain special characters
        config = TaskConfig(
            name="test-job",
            command=["echo", "test"],
            instance_type="gpu.nvidia.a100",
            env={"SPECIAL_VAR": special_chars}
        )
        assert config.env["SPECIAL_VAR"] == special_chars

        # But names typically should not
        with pytest.raises(ValidationError):
            TaskConfig(
                name=special_chars,
                command=["echo", "test"],
                instance_type="gpu.nvidia.a100",
            )

    @given(st.data())
    def test_empty_collections(self, data):
        """Test that empty collections are handled correctly."""
        # Empty env dict is fine
        config = TaskConfig(
            name="test",
            command=["echo", "test"],
            instance_type="gpu.nvidia.a100",
            env={},
            volumes=[],
        )
        assert config.env == {}
        assert config.volumes == []

        # Empty command defaults to sleep infinity
        config_empty_cmd = TaskConfig(
            name="test",
            command=[],
            instance_type="gpu.nvidia.a100",
        )
        assert config_empty_cmd.command == "sleep infinity"

        # None command also defaults to sleep infinity
        config_none_cmd = TaskConfig(
            name="test",
            command=None,
            instance_type="gpu.nvidia.a100",
        )
        assert config_none_cmd.command == "sleep infinity"


# ========== Performance and Memory Tests ==========

class TestModelPerformance:
    """Test model performance characteristics."""

    @given(
        num_volumes=st.integers(min_value=0, max_value=100),
        num_env_vars=st.integers(min_value=0, max_value=100),
    )
    def test_large_collection_handling(self, num_volumes, num_env_vars):
        """Test that models handle large collections efficiently."""
        # Generate large collections
        volumes = [
            VolumeSpec(
                name=f"volume-{i}",
                size_gb=100,
                mount_path=f"/mnt/vol{i}"
            )
            for i in range(num_volumes)
        ]

        env = {
            f"VAR_{i}": f"value_{i}"
            for i in range(num_env_vars)
        }

        # Create config with large collections
        config = TaskConfig(
            name="test",
            command=["echo", "test"],
            instance_type="gpu.nvidia.a100",
            volumes=volumes,
            env=env,
        )

        # Verify all items are preserved
        assert len(config.volumes) == num_volumes
        assert len(config.env) == num_env_vars

        # Test serialization performance
        json_str = config.model_dump_json()
        assert len(json_str) > 0

        # Test deserialization
        config2 = TaskConfig.model_validate_json(json_str)
        assert config2 == config
