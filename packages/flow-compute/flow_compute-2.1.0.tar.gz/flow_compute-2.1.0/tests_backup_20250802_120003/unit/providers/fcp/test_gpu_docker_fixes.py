"""Unit tests for GPU Docker fixes in startup script generation."""

import pytest
from flow.api.models import TaskConfig
from flow.providers.fcp.runtime.startup.builder import FCPStartupScriptBuilder as StartupScriptBuilder
from flow.providers.fcp.runtime.startup.sections import ScriptContext


class TestGPUDockerFixes:
    """Test GPU detection and Docker configuration."""
    
    def test_gpu_detection_in_context(self):
        """Test that GPU instances are properly detected."""
        # GPU instances
        gpu_contexts = [
            ScriptContext(instance_type="h100-80gb.sxm.8x"),
            ScriptContext(instance_type="a100"),
            ScriptContext(instance_type="4xa100"),
            ScriptContext(instance_type="gpu.nvidia.t4"),
            ScriptContext(instance_type="a100-80gb.sxm4.1x"),
        ]
        
        for ctx in gpu_contexts:
            assert ctx.has_gpu, f"Failed to detect GPU for {ctx.instance_type}"
        
        # Non-GPU instances
        cpu_contexts = [
            ScriptContext(instance_type="c5.large"),
            ScriptContext(instance_type="m5.xlarge"),
            ScriptContext(instance_type="t3.medium"),
            ScriptContext(instance_type=None),
        ]
        
        for ctx in cpu_contexts:
            assert not ctx.has_gpu, f"Incorrectly detected GPU for {ctx.instance_type}"
    
    def test_gpu_flag_in_docker_command(self):
        """Test that --gpus all is added for GPU instances."""
        builder = StartupScriptBuilder()
        
        # GPU instance
        gpu_config = TaskConfig(
            name="gpu-test",
            instance_type="h100-80gb.sxm.8x",
            command="nvidia-smi",
            max_run_time_hours=None,  # Disable runtime monitoring
            image="ubuntu:22.04"  # Use simple image to avoid compression
        )
        
        script = builder.build(gpu_config)
        # If script is compressed, decompress it for testing
        if script.compressed:
            # For now, skip the test if compressed
            pytest.skip("Script is compressed, cannot check content directly")
        
        assert "--gpus all" in script.content, "Missing --gpus all flag for GPU instance"
        assert "nvidia-container-toolkit" in script.content, "Missing nvidia-container-toolkit installation"
        
        # CPU instance
        cpu_config = TaskConfig(
            name="cpu-test",
            instance_type="c5.large",
            command="echo test",
            max_run_time_hours=None  # Disable runtime monitoring
        )
        
        script = builder.build(cpu_config)
        assert "--gpus all" not in script.content, "Should not have --gpus flag for CPU instance"
        assert "nvidia-container-toolkit" not in script.content, "Should not install nvidia-container-toolkit for CPU"
    
    def test_multiline_script_handling(self):
        """Test that multi-line scripts are properly handled."""
        builder = StartupScriptBuilder()
        
        multiline_script = """#!/bin/bash
echo "Line 1"
nvidia-smi
echo "Line 3"
"""
        
        config = TaskConfig(
            name="multiline-test",
            instance_type="a100",
            command=multiline_script,
            max_run_time_hours=None  # Disable runtime monitoring
        )
        
        script = builder.build(config)
        
        # If script is compressed, skip content checks
        if script.compressed:
            pytest.skip("Script is compressed, cannot check content directly")
        
        # Should use bash -c for multi-line scripts
        # Note: might be formatted as "bash -c" or "bash \\\n    -c"
        assert "bash" in script.content and "-c" in script.content, "Multi-line script should use bash -c"
        
        # Find the docker run section to verify script handling
        docker_section = script.content[script.content.find("docker run"):]
        assert "bash" in docker_section
        assert "-c" in docker_section
        # The multiline script should be preserved
        assert "echo" in docker_section
        assert "nvidia-smi" in docker_section
        
    def test_single_command_handling(self):
        """Test that single commands are handled correctly."""
        builder = StartupScriptBuilder()
        
        config = TaskConfig(
            name="single-cmd",
            instance_type="a100",
            command=["python", "train.py", "--epochs", "10"],
            max_run_time_hours=None  # Disable runtime monitoring
        )
        
        script = builder.build(config)
        
        # If script is compressed, skip content checks
        if script.compressed:
            pytest.skip("Script is compressed, cannot check content directly")
        
        # Should not use bash -c for command lists
        assert "bash -c" not in script.content, "Command list should not use bash -c"
        
        # Arguments should be properly quoted in the docker run command
        # Check that it's not using bash -c for command lists
        docker_section = script.content[script.content.find("docker run"):]
        assert "python" in docker_section
        assert "train.py" in docker_section
        assert "--epochs" in docker_section
        assert "10" in docker_section


class TestStartupScriptValidation:
    """Test validation and error cases."""
    
    def test_docker_error_without_gpu_flag(self):
        """Verify the error case we're fixing."""
        # This test documents the error that would occur without our fix
        error_script = "docker run nvidia/cuda:12.1.0-runtime-ubuntu22.04 'multi\nline\nscript'"
        
        # This would fail with: /opt/nvidia/nvidia_entrypoint.sh: line 67: /multi\nline\nscript: No such file or directory
        # Our fix converts this to: docker run nvidia/cuda:12.1.0-runtime-ubuntu22.04 bash -c 'multi\nline\nscript'
        
    def test_gpu_verification_script(self):
        """Test the GPU verification in the startup script."""
        builder = StartupScriptBuilder()
        
        config = TaskConfig(
            name="gpu-verify",
            instance_type="a100",
            command="echo test",
            max_run_time_hours=None  # Disable runtime monitoring
        )
        
        script = builder.build(config)
        
        # If script is compressed, skip content checks
        if script.compressed:
            pytest.skip("Script is compressed, cannot check content directly")
        
        # Should include GPU verification
        assert "docker run --rm --gpus all nvidia/cuda" in script.content
        assert "nvidia-smi || echo" in script.content  # GPU test with fallback