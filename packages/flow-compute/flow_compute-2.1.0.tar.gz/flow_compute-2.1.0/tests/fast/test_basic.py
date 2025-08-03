"""Basic smoke tests to verify test setup."""
from flow.api.models import TaskConfig, VolumeSpec
from flow.errors import FlowError, ValidationError


def test_import():
    """Test that we can import the main modules."""
    import flow
    assert flow.__version__ is not None


def test_task_config_creation():
    """Test basic TaskConfig creation."""
    config = TaskConfig(
        name="test-task",
        instance_type="a100.80gb.sxm4.1x",
        command="python test.py"
    )
    assert config.name == "test-task"
    assert config.instance_type == "a100.80gb.sxm4.1x"
    assert config.command == "python test.py"  # Command is preserved as string


def test_error_hierarchy():
    """Test error class hierarchy."""
    base_error = FlowError("test")
    validation_error = ValidationError("test")

    assert isinstance(base_error, Exception)
    assert isinstance(validation_error, FlowError)


def test_volume_spec():
    """Test VolumeSpec creation."""
    volume = VolumeSpec(size_gb=100, mount_path="/data")
    assert volume.size_gb == 100
    assert volume.mount_path == "/data"
