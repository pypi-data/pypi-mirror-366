"""Integration tests using a real SSH test server.

These tests verify SSH functionality with actual SSH connections
to a local test server, without requiring external infrastructure.
"""

from unittest.mock import Mock, patch

import pytest

try:
    import paramiko
except ImportError:
    pytest.skip("paramiko required for SSH server tests", allow_module_level=True)

from flow.api.models import Task, TaskConfig, TaskStatus
from tests.utils.ssh_test_server import SSHTestServer, create_test_client


class TestSSHWithRealServer:
    """Test SSH functionality with a real SSH server."""

    @pytest.fixture
    def ssh_server(self):
        """Create and start a test SSH server."""
        server = SSHTestServer(username="ubuntu", password="test")
        server.start()
        yield server
        server.stop()

    @pytest.fixture
    def task_with_test_server(self, ssh_server):
        """Create a task configured to use the test SSH server."""
        task = Task(
            task_id="test-ssh-task",
            name="ssh-test",
            status=TaskStatus.RUNNING,
            config=TaskConfig(
                name="ssh-test",
                instance_type="a100",
                command=["echo", "test"]
            ),
            created_at=datetime.now(timezone.utc),
            instance_type="a100",
            num_instances=1,
            region="us-central1-a",
            cost_per_hour="$10.00",
            ssh_host=ssh_server.address[0],
            ssh_port=ssh_server.address[1],
            ssh_user="ubuntu"
        )
        return task

    def test_ssh_connection_to_test_server(self, ssh_server):
        """Test that we can connect to the test SSH server."""
        client = create_test_client(ssh_server.address, username="ubuntu")

        # Execute a command
        stdin, stdout, stderr = client.exec_command("echo test")
        output = stdout.read().decode().strip()

        assert output == "test"
        client.close()

    def test_task_ssh_with_real_server(self, task_with_test_server, ssh_server):
        """Test task.ssh() with a real SSH server."""
        # Patch subprocess to use paramiko instead
        def mock_ssh_run(cmd, **kwargs):
            # Extract host, port, and command from ssh command
            # cmd format: ['ssh', '-p', 'port', 'user@host', 'command']
            if len(cmd) >= 5 and cmd[0] == "ssh":
                port = int(cmd[2])
                user_host = cmd[3]
                user = user_host.split("@")[0]
                command = " ".join(cmd[4:]) if len(cmd) > 4 else None

                # Use paramiko to execute
                client = create_test_client((ssh_server.address[0], port), user, "test")
                if command:
                    stdin, stdout, stderr = client.exec_command(command)
                    stdout.read()  # Wait for completion
                client.close()

                return Mock(returncode=0)
            return Mock(returncode=1)

        with patch('subprocess.run', side_effect=mock_ssh_run):
            # This should succeed
            task_with_test_server.ssh("echo test")

    def test_ssh_command_execution(self, ssh_server):
        """Test various command executions on the SSH server."""
        client = create_test_client(ssh_server.address, username="ubuntu")

        # Test hostname command
        stdin, stdout, stderr = client.exec_command("hostname")
        assert stdout.read().decode().strip() == "test-server"

        # Test log tailing (mocked)
        stdin, stdout, stderr = client.exec_command("tail -n 10 /var/log/test.log")
        output = stdout.read().decode()
        assert "Starting task" in output

        client.close()

    @pytest.mark.skip(reason="Excluded from parallel test execution due to hanging")
    def test_ssh_authentication_failure(self, ssh_server):
        """Test SSH authentication failure handling."""
        with pytest.raises(paramiko.AuthenticationException):
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=ssh_server.address[0],
                port=ssh_server.address[1],
                username="wrong_user",
                password="wrong_pass",
                timeout=5
            )

    @pytest.mark.timeout(30)
    def test_concurrent_ssh_connections(self, ssh_server):
        """Test multiple concurrent SSH connections."""
        clients = []

        # Create multiple connections
        for i in range(3):
            client = create_test_client(ssh_server.address, username="ubuntu")
            clients.append(client)

        # Execute commands on all
        for i, client in enumerate(clients):
            stdin, stdout, stderr = client.exec_command(f"echo client{i}")
            output = stdout.read().decode().strip()
            assert "Command executed: echo client" in output and str(i) in output

        # Close all
        for client in clients:
            client.close()


from datetime import datetime, timezone


class TestSSHServerIntegration:
    """Additional integration tests focusing on Flow SDK integration."""

    @pytest.fixture
    def ssh_server(self):
        """Create and start a test SSH server."""
        server = SSHTestServer(username="ubuntu", password="test")
        server.start()
        yield server
        server.stop()

    def test_log_retrieval_pattern(self, ssh_server):
        """Test the log retrieval pattern used by FCP provider."""
        client = create_test_client(ssh_server.address, username="ubuntu")

        # Simulate the FCP provider's log retrieval command
        log_command = "tail -n 100 /var/log/fcp/startup.log"
        stdin, stdout, stderr = client.exec_command(log_command)

        output = stdout.read().decode()
        assert output  # Server returns mock log data

        client.close()

    def test_ssh_timeout_handling(self, ssh_server):
        """Test SSH connection timeout handling."""
        # Stop server to simulate unavailable host
        ssh_server.stop()

        with pytest.raises(Exception):  # Could be socket.error or paramiko.SSHException
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname="127.0.0.1",
                port=ssh_server.port,
                username="ubuntu",
                password="test",
                timeout=1  # Short timeout
            )
