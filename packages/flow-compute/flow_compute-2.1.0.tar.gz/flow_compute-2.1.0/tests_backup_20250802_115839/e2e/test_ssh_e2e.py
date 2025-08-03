"""End-to-end SSH functionality tests with real FCP instances.

These tests verify SSH connectivity to actual GPU instances. Due to 10-20 minute
startup times, they are marked as slow and should be run selectively.

Run with: pytest -m slow tests/e2e/test_ssh_e2e.py
Skip with: pytest -m "not slow"
"""

import os
import subprocess
import time

import pytest

from flow import Flow
from flow.api.models import TaskConfig, TaskStatus
from flow.errors import FlowError


@pytest.mark.slow
@pytest.mark.e2e
class TestSSHEndToEnd:
    """End-to-end tests for SSH functionality with real FCP instances."""

    @pytest.fixture(scope="class")
    def flow(self):
        """Create Flow instance with proper configuration."""
        # Skip if not configured for E2E tests
        if not os.getenv("FLOW_E2E_TESTS_ENABLED"):
            pytest.skip("E2E tests not enabled. Set FLOW_E2E_TESTS_ENABLED=1")

        return Flow()

    @pytest.fixture(scope="class")
    def running_instance(self, flow):
        """Create and maintain a running instance for all SSH tests.
        
        This fixture starts an instance once and reuses it for all tests in the class,
        significantly reducing total test time.
        """
        config = TaskConfig(
            name="ssh-e2e-test-instance",
            instance_type="a100",  # Use smallest GPU instance
            command=["sleep", "3600"],  # Keep alive for 1 hour
            max_run_time_hours=1.0,
        )

        print("\nStarting test instance (this may take 10-20 minutes)...")
        start_time = time.time()

        task = flow.run(config)

        # Wait for instance to be ready with progress updates
        wait_interval = 30
        max_wait = 1800  # 30 minutes
        elapsed = 0

        while task.status != TaskStatus.RUNNING and elapsed < max_wait:
            time.sleep(wait_interval)
            task.refresh()
            elapsed = time.time() - start_time
            print(f"  Status: {task.status} (elapsed: {elapsed:.0f}s)")

        if task.status != TaskStatus.RUNNING:
            pytest.fail(f"Instance failed to start after {elapsed:.0f}s. Status: {task.status}")

        print(f"Instance ready after {elapsed:.0f}s")

        yield task

        # Cleanup
        try:
            task.stop()
        except Exception as e:
            print(f"Warning: Failed to stop test instance: {e}")

    def test_ssh_basic_connectivity(self, running_instance):
        """Test basic SSH connectivity to running instance."""
        # Test that we can connect and run a simple command
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
             "-p", str(running_instance.ssh_port),
             f"{running_instance.ssh_user}@{running_instance.ssh_host}",
             "echo 'SSH connection successful'"],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"SSH failed: {result.stderr}"
        assert "SSH connection successful" in result.stdout

    def test_ssh_command_execution(self, running_instance):
        """Test executing commands via task.ssh()."""
        # Test GPU visibility
        output = []

        def capture_output(line):
            output.append(line)

        # Monkey patch subprocess to capture output
        original_run = subprocess.run

        def mock_run(cmd, **kwargs):
            if "nvidia-smi" in cmd:
                # Capture the command for verification
                result = original_run(cmd, capture_output=True, text=True, **kwargs)
                if result.stdout:
                    output.append(result.stdout)
                return result
            return original_run(cmd, **kwargs)

        subprocess.run = mock_run

        try:
            # This should not raise an exception
            running_instance.ssh("nvidia-smi --query-gpu=name --format=csv,noheader")
        finally:
            subprocess.run = original_run

        # Verify GPU was detected
        assert any("A100" in line or "NVIDIA" in line for line in output), \
            f"GPU not detected in output: {output}"

    def test_ssh_environment_variables(self, running_instance):
        """Test SSH with custom environment variables."""
        # Test custom SSH user if configured
        custom_user = os.getenv("FCP_SSH_USER")
        if custom_user and custom_user != "ubuntu":
            assert running_instance.ssh_user == custom_user
        else:
            assert running_instance.ssh_user == "ubuntu"

        # Test custom SSH port if configured
        custom_port = os.getenv("FCP_SSH_PORT")
        if custom_port:
            assert running_instance.ssh_port == int(custom_port)
        else:
            assert running_instance.ssh_port == 22

    def test_ssh_file_operations(self, running_instance):
        """Test file operations over SSH."""
        test_content = "Flow SDK SSH test file"
        test_file = "/tmp/flow_ssh_test.txt"

        # Create file via SSH
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
             "-p", str(running_instance.ssh_port),
             f"{running_instance.ssh_user}@{running_instance.ssh_host}",
             f"echo '{test_content}' > {test_file}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0

        # Read file back
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
             "-p", str(running_instance.ssh_port),
             f"{running_instance.ssh_user}@{running_instance.ssh_host}",
             f"cat {test_file}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        assert test_content in result.stdout

    def test_ssh_startup_script_logs(self, running_instance):
        """Test accessing startup script logs via SSH."""
        # The log retrieval uses SSH internally
        logs = running_instance.logs(tail=50)

        # Verify we got some logs
        assert logs, "No logs retrieved"
        assert len(logs.splitlines()) <= 50, "Tail limit not respected"

    def test_ssh_long_running_command(self, running_instance):
        """Test SSH with long-running commands."""
        # Start a background process
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
             "-p", str(running_instance.ssh_port),
             f"{running_instance.ssh_user}@{running_instance.ssh_host}",
             "nohup sleep 60 & echo $!"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        pid = result.stdout.strip()
        assert pid.isdigit(), f"Invalid PID: {pid}"

        # Verify process is running
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
             "-p", str(running_instance.ssh_port),
             f"{running_instance.ssh_user}@{running_instance.ssh_host}",
             f"ps -p {pid} -o comm= | head -1"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        assert "sleep" in result.stdout

    @pytest.mark.skipif(
        not os.getenv("FLOW_TEST_MULTI_NODE"),
        reason="Multi-node tests require FLOW_TEST_MULTI_NODE=1"
    )
    def test_ssh_multi_node(self, flow):
        """Test SSH to multi-node tasks."""
        config = TaskConfig(
            name="ssh-multi-node-test",
            instance_type="a100",
            num_instances=2,
            command=["sleep", "600"],
            max_run_time_hours=0.5,
        )

        task = flow.run(config)

        try:
            # Wait for all instances
            max_wait = 1800
            start_time = time.time()
            while len(task.instances or []) < 2 and (time.time() - start_time) < max_wait:
                time.sleep(30)
                task.refresh()

            assert len(task.instances) == 2, f"Expected 2 instances, got {len(task.instances or [])}"

            # Test SSH to primary node
            task.ssh("hostname > /tmp/node0.txt")

            # Note: Multi-node SSH not fully implemented yet
            # When implemented, test would look like:
            # task.ssh("hostname > /tmp/node1.txt", node=1)

        finally:
            task.stop()


@pytest.mark.slow
@pytest.mark.e2e
def test_ssh_error_handling():
    """Test SSH error handling without starting an instance."""
    flow = Flow()

    # Create a task config but don't run it
    config = TaskConfig(
        name="ssh-error-test",
        instance_type="a100",
        command=["echo", "test"],
    )

    # Create a fake task that's not running
    from datetime import datetime, timezone

    from flow.api.models import Task

    fake_task = Task(
        task_id="fake-task-123",
        name="fake-task",
        status=TaskStatus.PENDING,
        config=config,
        created_at=datetime.now(timezone.utc),
        instance_type="a100",
        num_instances=1,
        region="us-central1-a",
        cost_per_hour="$0.00",
    )

    # Test SSH to non-running task
    with pytest.raises(FlowError) as exc_info:
        fake_task.ssh()

    assert "no SSH access available" in str(exc_info.value)
