"""Updated GPU Docker tests with proper task_id handling.

This version fixes the runtime monitoring validation issues.
"""

import pytest
from flow.api.models import TaskConfig
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder


class TestGPUDockerFixed:
    """Fixed GPU Docker configuration tests."""
    
    def test_gpu_driver_before_docker(self):
        """Test that GPU drivers are installed before Docker on GPU instances."""
        # Disable runtime monitoring to avoid task_id requirement
        gpu_config = TaskConfig(
            name="gpu-test",
            instance_type="h100-80gb.sxm.8x",
            command="nvidia-smi",
            max_run_time_hours=0  # Disable runtime monitoring
        )
        
        builder = StartupScriptBuilder()
        script = builder.build(gpu_config)
        
        # Should be valid without task_id since runtime monitoring is disabled
        assert script.is_valid, f"Script validation failed: {script.validation_errors}"
        
        lines = script.content.split('\n')
        
        # Find GPU and Docker setup sections
        gpu_section_idx = None
        docker_section_idx = None
        
        for i, line in enumerate(lines):
            if 'GPU Setup' in line or 'nvidia-driver' in line:
                if gpu_section_idx is None:
                    gpu_section_idx = i
            elif 'Docker setup' in line or 'Installing Docker' in line:
                if docker_section_idx is None:
                    docker_section_idx = i
        
        # GPU setup should come before Docker
        assert gpu_section_idx is not None, "GPU setup section not found"
        assert docker_section_idx is not None, "Docker setup section not found"
        assert gpu_section_idx < docker_section_idx, "GPU must be set up before Docker"
        
        # Should have nvidia-container-toolkit
        assert 'nvidia-container' in script.content or 'nvidia-docker' in script.content
    
    def test_cpu_instance_no_gpu_setup(self):
        """Test that CPU instances don't get GPU setup."""
        cpu_config = TaskConfig(
            name="cpu-test",
            instance_type="c5.large",
            command="echo test",
            max_run_time_hours=0  # Disable runtime monitoring
        )
        
        builder = StartupScriptBuilder()
        script = builder.build(cpu_config)
        
        assert script.is_valid
        
        # Should not have GPU setup
        assert 'nvidia-driver' not in script.content
        assert 'nvidia-container-toolkit' not in script.content
        
        # Should still have Docker
        assert 'Docker' in script.content or 'docker' in script.content
    
    def test_gpu_with_runtime_monitoring(self):
        """Test GPU setup with runtime monitoring enabled."""
        config = TaskConfig(
            name="gpu-runtime-test",
            instance_type="a100-40gb",
            command="python train.py",
            max_run_time_hours=2.0,  # Enable runtime monitoring
        )
        
        # Add task_id to config for runtime monitoring
        setattr(config, 'task_id', 'gpu-test-123')
        
        builder = StartupScriptBuilder()
        script = builder.build(config)
        
        # Should be valid with task_id provided
        assert script.is_valid, f"Script validation failed: {script.validation_errors}"
        
        # Should have both GPU setup and runtime monitoring
        assert 'nvidia' in script.content.lower()
        assert 'runtime' in script.content.lower() or 'monitoring' in script.content.lower()
    
    def test_gpu_docker_daemon_config(self):
        """Test Docker daemon configuration for GPU support."""
        config = TaskConfig(
            name="gpu-daemon-test",
            instance_type="h100",
            image="nvidia/cuda:12.0-runtime",
            command="nvidia-smi",
            max_run_time_hours=0,
        )
        
        builder = StartupScriptBuilder()
        script = builder.build(config)
        
        assert script.is_valid
        
        # Should configure Docker daemon for GPU
        assert 'daemon.json' in script.content
        assert 'nvidia' in script.content
    
    @pytest.mark.parametrize("instance_type,should_have_gpu", [
        ("h100", True),
        ("h100-80gb", True),
        ("a100-40gb", True),
        ("a100-80gb.sxm.8x", True),
        ("a10g", True),
        ("t4", True),
        ("c5.large", False),
        ("m5.xlarge", False),
        ("r5.2xlarge", False),
    ])
    def test_gpu_detection_by_instance_type(self, instance_type, should_have_gpu):
        """Test GPU detection based on instance type."""
        config = TaskConfig(
            name=f"test-{instance_type}",
            instance_type=instance_type,
            command="echo test",
            max_run_time_hours=0,
        )
        
        builder = StartupScriptBuilder()
        script = builder.build(config)
        
        assert script.is_valid
        
        has_gpu_setup = 'nvidia' in script.content.lower()
        
        if should_have_gpu:
            assert has_gpu_setup, f"{instance_type} should have GPU setup"
        else:
            assert not has_gpu_setup, f"{instance_type} should not have GPU setup"


# Helper function to create configs with task_id when needed
def create_gpu_config_with_monitoring(name: str, instance_type: str, hours: float) -> TaskConfig:
    """Create GPU config with runtime monitoring and task_id."""
    config = TaskConfig(
        name=name,
        instance_type=instance_type,
        command="python gpu_task.py",
        max_run_time_hours=hours,
    )
    
    # Add task_id for runtime monitoring
    setattr(config, 'task_id', f"{name}-{instance_type}-id")
    
    return config


# Test using the helper
def test_gpu_lifecycle_with_monitoring():
    """Test complete GPU task lifecycle with monitoring."""
    config = create_gpu_config_with_monitoring(
        name="gpu-lifecycle",
        instance_type="a100-80gb",
        hours=4.0
    )
    
    builder = StartupScriptBuilder()
    script = builder.build(config)
    
    assert script.is_valid
    assert 'nvidia' in script.content
    assert 'runtime limit' in script.content.lower()
    assert hasattr(config, 'task_id')  # Verify task_id was added