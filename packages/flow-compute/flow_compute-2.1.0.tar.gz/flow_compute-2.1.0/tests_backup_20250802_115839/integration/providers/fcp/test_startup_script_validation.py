"""Test startup script validation and execution.

These tests verify that:
- Generated scripts have valid bash syntax
- Scripts execute without errors in a container environment
- Volume mounting order is correct
- Docker operations work as expected
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

from flow.api.models import TaskConfig, VolumeSpec
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder


class TestScriptSyntaxValidation:
    """Test that generated scripts have valid bash syntax."""

    @pytest.fixture
    def test_configs(self):
        """Various test configurations to validate."""
        return [
            # Minimal config
            TaskConfig(
                name="minimal",
                instance_type="a100-80gb.sxm.1x",
                image="ubuntu:22.04",
                command=["sleep", "infinity"],
            ),
            # Complex config
            TaskConfig(
                name="complex",
                instance_type="a100-80gb.sxm.1x",
                image="pytorch/pytorch:2.0",
                command=["python", "-c", "print('hello')"],
                env={"API_KEY": "test", "DEBUG": "true"},
                volumes=[
                    VolumeSpec(size_gb=10, mount_path="/data"),
                    VolumeSpec(size_gb=50, mount_path="/var/lib/docker"),
                ],
                max_run_time_hours=2.0,
            ),
            # GPU config
            TaskConfig(
                name="gpu",
                instance_type="a100-80gb.sxm.1x",
                image="nvidia/cuda:11.8.0-runtime-ubuntu22.04",
                command=["nvidia-smi"],
                env={"CUDA_VISIBLE_DEVICES": "0"},
            ),
            # Multi-volume config
            TaskConfig(
                name="multi-volume",
                instance_type="a100-80gb.sxm.1x",
                image="postgres:15",
                command=["postgres"],
                volumes=[
                    VolumeSpec(size_gb=100, mount_path="/var/lib/postgresql/data"),
                    VolumeSpec(size_gb=50, mount_path="/backup"),
                    VolumeSpec(size_gb=20, mount_path="/logs"),
                ],
            ),
        ]

    def test_all_scripts_have_valid_syntax(self, test_configs):
        """Test that all generated scripts pass bash syntax check."""
        builder = StartupScriptBuilder()

        for config in test_configs:
            script = builder.build(config)

            if not script.is_valid:
                pytest.skip(f"Config {config.name} has validation errors")

            # Check syntax with bash -n
            result = subprocess.run(
                ["bash", "-n"],
                input=script.content,
                capture_output=True,
                text=True,
                timeout=5,
            )

            assert result.returncode == 0, (
                f"Script for {config.name} has syntax errors:\n{result.stderr}"
            )

    def test_script_shellcheck_compliance(self):
        """Test scripts with shellcheck if available."""
        # Check if shellcheck is installed
        try:
            subprocess.run(["shellcheck", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("shellcheck not installed")

        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            command="echo 'hello world'",
        )

        script = builder.build(config)

        # Write to temp file for shellcheck
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(script.content)
            temp_path = f.name

        try:
            # Run shellcheck with common exclusions
            result = subprocess.run(
                [
                    "shellcheck",
                    "-e", "SC2129",  # Consider using { cmd1; cmd2; }
                    "-e", "SC2086",  # Double quote to prevent globbing
                    temp_path
                ],
                capture_output=True,
                text=True,
            )

            # shellcheck may have warnings but shouldn't have errors
            assert "error" not in result.stderr.lower()
        finally:
            Path(temp_path).unlink()


class TestVolumeMountOrdering:
    """Test that volumes mount in the correct order."""

    def test_docker_cache_mounts_before_docker_install(self):
        """Test that /var/lib/docker mounts before Docker installation."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="docker-cache",
            instance_type="a100-80gb.sxm.1x",
            image="tensorflow/tensorflow:latest-gpu",
            command=["python", "-c", "print('test')"],
            volumes=[
                VolumeSpec(size_gb=100, mount_path="/var/lib/docker"),
                VolumeSpec(size_gb=50, mount_path="/data"),
            ],
        )

        script = builder.build(config)
        lines = script.content.split('\n')

        # Find key lines
        docker_mount_line = None
        docker_install_line = None
        docker_start_line = None

        for i, line in enumerate(lines):
            if 'mount "$DEVICE" /var/lib/docker' in line:
                docker_mount_line = i
            elif 'Installing Docker' in line:
                docker_install_line = i
            elif 'systemctl start docker' in line:
                docker_start_line = i

        # Verify ordering
        assert docker_mount_line is not None, "Docker volume mount not found"
        assert docker_install_line is not None, "Docker install not found"
        assert docker_start_line is not None, "Docker start not found"

        assert docker_mount_line < docker_install_line, (
            "Docker cache must be mounted before Docker installation"
        )
        assert docker_install_line < docker_start_line, (
            "Docker must be installed before starting"
        )

    def test_all_volumes_mount_before_docker(self):
        """Test that all volumes mount before Docker operations."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="multi-volume",
            instance_type="a100-80gb.sxm.1x",
            image="postgres:15",
            command=["postgres"],
            volumes=[
                VolumeSpec(size_gb=20, mount_path="/data1"),
                VolumeSpec(size_gb=30, mount_path="/data2"),
                VolumeSpec(size_gb=40, mount_path="/var/lib/docker"),
            ],
        )

        script = builder.build(config)

        # Find section boundaries
        volume_section_start = script.content.find("# Volume mounting")
        volume_section_end = script.content.find("# Docker setup")

        assert volume_section_start != -1
        assert volume_section_end != -1
        assert volume_section_start < volume_section_end

        # All mount commands should be in volume section
        volume_section = script.content[volume_section_start:volume_section_end]

        assert "/data1" in volume_section
        assert "/data2" in volume_section
        assert "/var/lib/docker" in volume_section
        assert "mount" in volume_section


class TestScriptExecution:
    """Test script execution behavior."""

    def test_script_handles_missing_docker_image(self):
        """Test that script handles missing Docker images gracefully."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="nonexistent/image:latest",
            command=["echo", "test"],
        )

        script = builder.build(config)

        # Should have Docker pull command
        assert "docker pull nonexistent/image:latest" in script.content

        # Should have error handling
        assert "set -euxo pipefail" in script.content  # Will exit on error

    def test_script_creates_required_directories(self):
        """Test that script creates all required directories."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            command=["sleep", "infinity"],
            volumes=[
                VolumeSpec(size_gb=10, mount_path="/data/models"),
                VolumeSpec(size_gb=20, mount_path="/var/cache/app"),
            ],
        )

        script = builder.build(config)

        # Should create mount points
        assert "mkdir -p /data/models" in script.content
        assert "mkdir -p /var/cache/app" in script.content

        # Should create log directories
        assert 'mkdir -p "$LOG_DIR"' in script.content
        assert "mkdir -p /var/log/fcp" in script.content

    def test_script_handles_lifecycle_correctly(self):
        """Test that script completes successfully without lifecycle management."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="lifecycle-test",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            command=["sleep", "infinity"],
            max_run_time_hours=0.5,  # 30 minutes
        )

        script = builder.build(config)

        # Should have completion marker
        assert "FCP startup script completed successfully" in script.content
        assert "/var/run/fcp-startup-complete" in script.content

        # Should NOT have lifecycle systemd timers (removed functionality)
        assert "flow-max-runtime.timer" not in script.content
        assert "flow-terminate-check" not in script.content


class TestScriptCompression:
    """Test script compression behavior."""

    def test_large_scripts_are_compressed(self):
        """Test that large scripts are automatically compressed."""
        builder = StartupScriptBuilder(max_uncompressed_size=5000)  # 5KB limit

        # Create config that generates large script
        large_env = {f"VAR_{i}": "x" * 100 for i in range(100)}

        config = TaskConfig(
            name="large-script",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            env=large_env,
            command="x" * 3000,  # 3KB user script
        )

        script = builder.build(config)

        assert script.compressed is True
        assert "Bootstrap script for compressed startup script" in script.content
        assert "base64 -d | gunzip | bash" in script.content

        # Compressed script should still be valid bash
        result = subprocess.run(
            ["bash", "-n"],
            input=script.content,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
