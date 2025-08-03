"""Test Docker-specific functionality in startup scripts.

These tests focus on:
- Docker image caching behavior
- Volume persistence for Docker storage
- Docker command generation
- Container lifecycle management
"""


from flow.api.models import TaskConfig, VolumeSpec
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder


class TestDockerImageCaching:
    """Test Docker image caching functionality."""

    def test_docker_cache_volume_configuration(self):
        """Test that Docker cache volume is configured correctly."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="cache-test",
            instance_type="a100-80gb.sxm.1x",
            image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
            command=["python", "-c", "print('test')"],
            volumes=[
                VolumeSpec(size_gb=100, mount_path="/var/lib/docker"),
            ],
            max_run_time_hours=0,  # Disable runtime monitoring for this test
        )

        script = builder.build(config)

        # Verify volume mounting happens before Docker
        assert "/var/lib/docker" in script.content

        # Check mount command structure
        assert 'mount "$DEVICE" /var/lib/docker' in script.content

        # Verify Docker installation comes after
        docker_mount_pos = script.content.find("mount")
        docker_install_pos = script.content.find("Installing Docker")
        assert docker_mount_pos < docker_install_pos

    def test_docker_pull_command_generation(self):
        """Test Docker pull command is generated correctly."""
        builder = StartupScriptBuilder()
        test_images = [
            "ubuntu:22.04",
            "pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
            "nvcr.io/nvidia/tensorflow:23.09-tf2-py3",
            "myregistry.com:5000/myapp:v1.2.3",
        ]

        for image in test_images:
            config = TaskConfig(
                name="test",
                instance_type="a100-80gb.sxm.1x",
                image=image,
                command=["echo", "test"],
            )

            script = builder.build(config)

            assert f"docker pull {image}" in script.content
            assert f'echo "Checking Docker image: {image}"' in script.content

    def test_docker_run_with_cache_volumes(self):
        """Test Docker run command includes cache volume mounts."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="tensorflow/tensorflow:latest-gpu",
            command=["python", "-c", "print('test')"],
            volumes=[
                VolumeSpec(size_gb=100, mount_path="/var/lib/docker"),
                VolumeSpec(size_gb=50, mount_path="/data"),
                VolumeSpec(size_gb=20, mount_path="/models"),
            ],
        )

        script = builder.build(config)

        # Check docker run command includes volume mounts
        # Find the full docker run command (may be multi-line)
        docker_start = script.content.find("docker run")
        docker_end = script.content.find("tensorflow/tensorflow:latest-gpu", docker_start) + len("tensorflow/tensorflow:latest-gpu")
        docker_run_section = script.content[docker_start:docker_end]
        assert "-v /data:/data" in docker_run_section
        assert "-v /models:/models" in docker_run_section
        # Should NOT mount /var/lib/docker inside container
        assert "-v /var/lib/docker:/var/lib/docker" not in docker_run_section

    def test_docker_logging_configuration(self):
        """Test Docker logging is configured properly."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="nginx:latest",
            command=["nginx", "-g", "daemon off;"],
        )

        script = builder.build(config)

        # Check logging configuration
        assert "--log-driver=json-file" in script.content
        assert "--log-opt max-size=100m" in script.content
        assert "--log-opt max-file=3" in script.content

        # Check log viewing commands
        assert "docker logs main --tail 50" in script.content


class TestDockerStartupBehavior:
    """Test Docker startup and lifecycle behavior."""

    def test_docker_daemon_startup_sequence(self):
        """Test Docker daemon startup follows correct sequence."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            command=["sleep", "infinity"],
        )

        script = builder.build(config)

        # Check startup sequence
        sequence = [
            "systemctl enable docker",
            "systemctl start docker",
            "timeout 30 sh -c 'until docker info",
            "docker pull",
            "docker run",
        ]

        positions = []
        for step in sequence:
            pos = script.content.find(step)
            assert pos != -1, f"Missing step: {step}"
            positions.append(pos)

        # Verify order
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"Step {sequence[i]} should come before {sequence[i + 1]}"
            )

    def test_docker_restart_policy(self):
        """Test Docker container restart policy."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="redis:7",
            command=["redis-server"],
        )

        script = builder.build(config)

        assert "--restart=unless-stopped" in script.content

    def test_docker_container_naming(self):
        """Test Docker container naming convention."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="my-test-task",
            instance_type="a100-80gb.sxm.1x",
            image="postgres:15",
            command=["postgres"],
        )

        script = builder.build(config)

        # Should use consistent container name
        assert "--name=main" in script.content
        assert "docker logs main" in script.content
        assert "docker ps" in script.content


class TestDockerEnvironmentHandling:
    """Test Docker environment variable handling."""

    def test_environment_variables_passed_to_docker(self):
        """Test environment variables are passed to Docker correctly."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="postgres:15",
            command=["postgres"],
            env={
                "POSTGRES_PASSWORD": "mysecret",
                "POSTGRES_USER": "myuser",
                "POSTGRES_DB": "mydb",
                "CUSTOM_VAR": "value with spaces",
            },
        )

        script = builder.build(config)

        # Check environment variables are passed
        assert '-e POSTGRES_PASSWORD="mysecret"' in script.content
        assert '-e POSTGRES_USER="myuser"' in script.content
        assert '-e POSTGRES_DB="mydb"' in script.content
        assert '-e CUSTOM_VAR="value with spaces"' in script.content

    def test_gpu_environment_setup(self):
        """Test GPU-specific environment setup."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="gpu-test",
            instance_type="a100-80gb.sxm.1x",
            image="nvidia/cuda:11.8.0-runtime-ubuntu22.04",
            command=["nvidia-smi"],
            env={
                "CUDA_VISIBLE_DEVICES": "0,1",
            },
        )

        script = builder.build(config)

        assert '-e CUDA_VISIBLE_DEVICES="0,1"' in script.content


class TestDockerCommandGeneration:
    """Test Docker command generation."""

    def test_docker_command_with_arguments(self):
        """Test Docker run with custom command and arguments."""
        builder = StartupScriptBuilder()
        test_cases = [
            (["python", "train.py"], "python train.py"),
            (["python", "-m", "torch.distributed.launch"], "python -m torch.distributed.launch"),
            (["bash", "-c", "echo hello && sleep 10"], 'bash -c echo hello && sleep 10'),
        ]

        for command, expected in test_cases:
            config = TaskConfig(
                name="test",
                instance_type="a100-80gb.sxm.1x",
                image="python:3.11",
                command=command,
            )

            script = builder.build(config)

            # Command should appear in docker run
            assert "python:3.11" in script.content
            # Check the command appears correctly in the script
            # The docker run command is multi-line, so check for the components
            docker_start = script.content.find("docker run")
            docker_end = script.content.find("python:3.11", docker_start) + 200  # Look ahead for command
            docker_section = script.content[docker_start:docker_end]
            # Command args should be properly quoted
            import shlex
            for arg in command:
                assert shlex.quote(arg) in docker_section

    def test_docker_port_mapping(self):
        """Test Docker port mapping generation."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="nginx:latest",
            command=["nginx", "-g", "daemon off;"],
        )

        # Note: ports would come from a different source in real usage
        # For now, testing with ScriptContext directly
        from flow.providers.fcp.runtime.startup.sections import DockerSection, ScriptContext

        section = DockerSection()
        context = ScriptContext(
            docker_image="nginx:latest",
            ports=[80, 443, 8080],
        )

        content = section.generate(context)

        assert "-p 80:80" in content
        assert "-p 443:443" in content
        assert "-p 8080:8080" in content


class TestDockerErrorHandling:
    """Test Docker error handling in startup scripts."""

    def test_docker_installation_error_handling(self):
        """Test that Docker installation errors are handled."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            command=["sleep", "infinity"],
        )

        script = builder.build(config)

        # Script should exit on errors due to set -e
        assert "set -euxo pipefail" in script.content

        # Docker readiness check
        assert "timeout 30" in script.content
        assert "until docker info" in script.content

    def test_volume_mount_error_handling(self):
        """Test volume mount error handling."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test",
            instance_type="a100-80gb.sxm.1x",
            image="ubuntu:22.04",
            command=["sleep", "infinity"],
            volumes=[
                VolumeSpec(size_gb=10, mount_path="/data"),
            ],
        )

        script = builder.build(config)

        # Should wait for device
        assert "while [ ! -b \"$DEVICE\" ]" in script.content
        assert "TIMEOUT=60" in script.content

        # Should exit on timeout
        assert 'echo "ERROR: Device $DEVICE not found' in script.content
        assert "exit 1" in script.content
