"""Test individual script sections in isolation."""

from flow.providers.fcp.runtime.startup.sections import (
    CompletionSection,
    DockerSection,
    HeaderSection,
    PortForwardingSection,
    ScriptContext,
    UserScriptSection,
    VolumeSection,
)


class TestHeaderSection:
    """Test the header section in isolation."""

    def test_generate_basic_header(self):
        """Test basic header generation."""
        section = HeaderSection()
        context = ScriptContext()

        content = section.generate(context)

        # Explicit assertions on critical components
        assert "#!/bin/bash" in content
        assert "set -euxo pipefail" in content
        assert "FCP_BID_ID" in content
        assert "LOG_DIR=\"/var/log/flow\"" in content
        assert "STDOUT_LOG=\"$LOG_DIR/$TASK_ID.out\"" in content
        assert "STDERR_LOG=\"$LOG_DIR/$TASK_ID.err\"" in content

    def test_should_always_include(self):
        """Header should always be included."""
        section = HeaderSection()
        assert section.should_include(ScriptContext()) is True

    def test_priority_is_first(self):
        """Header should have lowest priority number."""
        section = HeaderSection()
        assert section.priority == 10

    def test_name(self):
        """Test section name."""
        section = HeaderSection()
        assert section.name == "header"

    def test_no_validation_errors(self):
        """Header section should never have validation errors."""
        section = HeaderSection()
        context = ScriptContext()
        assert section.validate(context) == []


class TestVolumeSection:
    """Test volume mounting section."""

    def test_no_volumes_no_content(self):
        """Test that no content is generated without volumes."""
        section = VolumeSection()
        context = ScriptContext(volumes=[])

        content = section.generate(context)
        assert content == ""

    def test_should_not_include_without_volumes(self):
        """Should not include section without volumes."""
        section = VolumeSection()
        context = ScriptContext(volumes=[])
        assert section.should_include(context) is False

    def test_single_volume_mount(self):
        """Test mounting a single volume."""
        section = VolumeSection()
        context = ScriptContext(
            volumes=[{"mount_path": "/data", "size_gb": 10}]
        )

        content = section.generate(context)

        # Check critical mount components
        assert "Volume mounting" in content
        assert "/dev/xvdf" in content  # First volume device
        assert "mkdir -p /data" in content
        assert 'mount "$DEVICE" /data' in content
        assert "mkfs.ext4 -F" in content
        assert "/etc/fstab" in content

    def test_multiple_volume_mounts(self):
        """Test mounting multiple volumes."""
        section = VolumeSection()
        context = ScriptContext(
            volumes=[
                {"mount_path": "/data1", "size_gb": 10},
                {"mount_path": "/data2", "size_gb": 20},
                {"mount_path": "/data3", "size_gb": 30},
            ]
        )

        content = section.generate(context)

        # Check all volumes are handled
        assert "/dev/xvdf" in content  # First volume
        assert "/dev/xvdg" in content  # Second volume
        assert "/dev/xvdh" in content  # Third volume
        assert "/data1" in content
        assert "/data2" in content
        assert "/data3" in content

    def test_docker_cache_volume(self):
        """Test mounting volume at Docker storage location."""
        section = VolumeSection()
        context = ScriptContext(
            volumes=[{"mount_path": "/var/lib/docker", "size_gb": 50}]
        )

        content = section.generate(context)

        assert "/var/lib/docker" in content
        assert "mkdir -p /var/lib/docker" in content

    def test_validate_too_many_volumes(self):
        """Test validation for too many volumes."""
        section = VolumeSection()
        # AWS limit is 20 additional volumes
        context = ScriptContext(
            volumes=[{"mount_path": f"/data{i}"} for i in range(25)]
        )

        errors = section.validate(context)
        assert len(errors) == 1
        assert "Too many volumes: 25" in errors[0]

    def test_validate_invalid_mount_path(self):
        """Test validation for invalid mount paths."""
        section = VolumeSection()
        context = ScriptContext(
            volumes=[{"mount_path": "data"}]  # Not absolute
        )

        errors = section.validate(context)
        assert len(errors) == 1
        assert "mount_path must be absolute" in errors[0]

    def test_priority(self):
        """Test volume section priority."""
        section = VolumeSection()
        assert section.priority == 30  # Before Docker

    def test_name(self):
        """Test section name."""
        section = VolumeSection()
        assert section.name == "volumes"


class TestDockerSection:
    """Test Docker installation and container management."""

    def test_no_image_no_content(self):
        """Test that no content is generated without Docker image."""
        section = DockerSection()
        context = ScriptContext(docker_image=None)

        content = section.generate(context)
        assert content == ""

    def test_should_not_include_without_image(self):
        """Should not include section without Docker image."""
        section = DockerSection()
        context = ScriptContext(docker_image=None)
        assert section.should_include(context) is False

    def test_basic_docker_setup(self):
        """Test basic Docker setup and run."""
        section = DockerSection()
        context = ScriptContext(docker_image="ubuntu:22.04")

        content = section.generate(context)

        # Check Docker installation
        assert "Installing Docker" in content
        assert "curl -fsSL https://get.docker.com" in content
        assert "systemctl enable docker" in content
        assert "systemctl start docker" in content

        # Check image pull and run
        assert "docker pull ubuntu:22.04" in content
        assert "docker run" in content
        assert "--name=main" in content
        assert "--restart=unless-stopped" in content
        assert "ubuntu:22.04" in content

    def test_docker_with_ports(self):
        """Test Docker run with port mappings."""
        section = DockerSection()
        context = ScriptContext(
            docker_image="nginx",
            ports=[80, 443, 8080]
        )

        content = section.generate(context)

        assert "-p 80:80" in content
        assert "-p 443:443" in content
        assert "-p 8080:8080" in content

    def test_docker_with_volumes(self):
        """Test Docker run with volume mounts."""
        section = DockerSection()
        context = ScriptContext(
            docker_image="postgres:15",
            volumes=[
                {"mount_path": "/var/lib/postgresql/data"},
                {"mount_path": "/backup"},
            ]
        )

        content = section.generate(context)

        assert "-v /var/lib/postgresql/data:/var/lib/postgresql/data" in content
        assert "-v /backup:/backup" in content

    def test_docker_with_environment(self):
        """Test Docker run with environment variables."""
        section = DockerSection()
        context = ScriptContext(
            docker_image="mysql:8",
            environment={
                "MYSQL_ROOT_PASSWORD": "secret",
                "MYSQL_DATABASE": "myapp",
            }
        )

        content = section.generate(context)

        assert '-e MYSQL_ROOT_PASSWORD="secret"' in content
        assert '-e MYSQL_DATABASE="myapp"' in content

    def test_docker_with_command(self):
        """Test Docker run with custom command."""
        section = DockerSection()
        context = ScriptContext(
            docker_image="python:3.11",
            docker_command=["python", "-m", "http.server", "8000"]
        )

        content = section.generate(context)

        # Check that the image and command components are present
        assert "python:3.11" in content
        assert "python" in content
        assert "-m" in content
        assert "http.server" in content
        assert "8000" in content

    def test_validate_unofficial_image_warning(self):
        """Test validation warns about unofficial images."""
        section = DockerSection()
        context = ScriptContext(docker_image="myapp")

        errors = section.validate(context)
        assert len(errors) == 1
        assert "should include registry/namespace" in errors[0]

    def test_validate_official_images_pass(self):
        """Test validation passes for official Docker images."""
        section = DockerSection()
        official_images = ["ubuntu", "nginx", "redis", "postgres", "python"]

        for image in official_images:
            context = ScriptContext(docker_image=image)
            errors = section.validate(context)
            assert len(errors) == 0

    def test_priority(self):
        """Test Docker section priority."""
        section = DockerSection()
        assert section.priority == 40  # After volumes

    def test_name(self):
        """Test section name."""
        section = DockerSection()
        assert section.name == "docker"


class TestPortForwardingSection:
    """Test port forwarding configuration."""

    def test_no_ports_no_content(self):
        """Test that no content is generated without ports."""
        section = PortForwardingSection()
        context = ScriptContext(ports=[])

        content = section.generate(context)
        assert content == ""

    def test_single_port_forwarding(self):
        """Test forwarding a single port."""
        section = PortForwardingSection()
        context = ScriptContext(ports=[8080])

        content = section.generate(context)

        # Check nginx installation
        assert "apt-get install -y -qq nginx" in content

        # Check nginx config
        assert "listen 8080;" in content
        assert "proxy_pass http://127.0.0.1:8080;" in content
        assert "/etc/nginx/sites-available/port8080" in content

        # Check foundrypf service
        assert "foundrypf.service" in content
        assert "systemctl enable foundrypf" in content

    def test_multiple_ports(self):
        """Test forwarding multiple ports."""
        section = PortForwardingSection()
        context = ScriptContext(ports=[80, 443, 8080])

        content = section.generate(context)

        assert "listen 80;" in content
        assert "listen 443;" in content
        assert "listen 8080;" in content
        assert content.count("proxy_pass") == 3

    def test_validate_invalid_ports(self):
        """Test validation for invalid port numbers."""
        section = PortForwardingSection()
        context = ScriptContext(ports=[0, 70000, -1, 80])

        errors = section.validate(context)
        assert len(errors) == 3
        assert "Invalid port number: 0" in str(errors)
        assert "Invalid port number: 70000" in str(errors)
        assert "Invalid port number: -1" in str(errors)

    def test_priority(self):
        """Test port forwarding section priority."""
        section = PortForwardingSection()
        assert section.priority == 20  # Early, before volumes

    def test_name(self):
        """Test section name."""
        section = PortForwardingSection()
        assert section.name == "port_forwarding"


class TestUserScriptSection:
    """Test user-provided script execution."""

    def test_no_script_no_content(self):
        """Test that no content is generated without user script."""
        section = UserScriptSection()
        context = ScriptContext(user_script=None)

        content = section.generate(context)
        assert content == ""

    def test_empty_script_no_content(self):
        """Test that empty script generates no content."""
        section = UserScriptSection()
        context = ScriptContext(user_script="   \n  \n  ")

        content = section.generate(context)
        assert content == ""

    def test_user_script_execution(self):
        """Test user script is properly wrapped."""
        section = UserScriptSection()
        user_code = """apt-get update
apt-get install -y python3-pip
pip install numpy pandas"""

        context = ScriptContext(user_script=user_code)
        content = section.generate(context)

        # Check script is wrapped properly
        assert "User startup script" in content
        assert "cat > /tmp/user_startup.sh <<'USER_SCRIPT_EOF'" in content
        assert "#!/bin/bash" in content  # Should add shebang
        assert user_code in content
        assert "USER_SCRIPT_EOF" in content
        assert "chmod +x /tmp/user_startup.sh" in content
        assert "/tmp/user_startup.sh" in content

    def test_user_script_adds_shebang_when_missing(self):
        """Test that shebang is added when not present."""
        section = UserScriptSection()
        user_code = """echo "Hello World"
echo "This script has no shebang"
"""
        context = ScriptContext(user_script=user_code)
        content = section.generate(context)

        # Check that shebang is added
        assert "#!/bin/bash\necho \"Hello World\"" in content
        assert content.count("#!/bin/bash") == 1

    def test_user_script_preserves_existing_shebang(self):
        """Test that existing shebang is preserved."""
        section = UserScriptSection()
        user_code = """#!/usr/bin/env python3
print("Hello from Python")
print("This script already has a shebang")
"""
        context = ScriptContext(user_script=user_code)
        content = section.generate(context)

        # Check that original shebang is preserved
        assert "#!/usr/bin/env python3" in content
        # Should not add bash shebang
        assert "#!/bin/bash" not in content
        assert content.count("#!/usr/bin/env python3") == 1

    def test_priority(self):
        """Test user script section priority."""
        section = UserScriptSection()
        assert section.priority == 90  # Near the end

    def test_name(self):
        """Test section name."""
        section = UserScriptSection()
        assert section.name == "user_script"


class TestCompletionSection:
    """Test startup completion section."""

    def test_should_always_include(self):
        """Completion should always be included."""
        section = CompletionSection()
        assert section.should_include(ScriptContext()) is True

    def test_completion_content(self):
        """Test completion section content."""
        section = CompletionSection()
        context = ScriptContext()

        content = section.generate(context)

        # Check completion markers
        assert "FCP startup script completed successfully" in content
        assert "touch /var/run/fcp-startup-complete" in content

        # Check system info logging
        assert "uname -a" in content
        assert "df -h" in content
        assert "free -h" in content

    def test_priority_is_last(self):
        """Completion should have highest priority number."""
        section = CompletionSection()
        assert section.priority == 100

    def test_name(self):
        """Test section name."""
        section = CompletionSection()
        assert section.name == "completion"
