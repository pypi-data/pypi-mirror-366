"""Integration tests for SSH functionality using the local provider.

These are true integration tests that verify SSH configuration is properly
set up when using the local provider, without mocking internal implementation.
"""


import pytest

from flow import Flow
from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.providers.local.provider import LocalProvider


class TestSSHWithLocalProvider:
    """Test SSH integration with the local provider."""

    @pytest.fixture
    def local_config(self):
        """Create config for local provider."""
        return Config(
            provider="local",
            provider_config={},
            auth_token="local-test"
        )

    @pytest.fixture
    def local_provider(self, local_config):
        """Create a local provider instance."""
        return LocalProvider(local_config)

    def test_local_provider_sets_ssh_fields(self, local_provider):
        """Test that local provider properly sets SSH fields on tasks."""
        config = TaskConfig(
            name="local-ssh-test",
            instance_type="a100",
            command=["echo", "hello from local"]
        )

        # Submit task to local provider
        task = local_provider.submit_task(
            instance_type="a100",
            config=config
        )

        # Verify SSH fields are set
        assert task.ssh_host == "localhost"
        assert isinstance(task.ssh_port, int)
        assert task.ssh_port >= 22000  # Local provider uses ports 22000+
        assert task.ssh_user == "flow"

        # Verify task is created properly
        assert task.task_id.startswith("local-")
        assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

    def test_multiple_tasks_get_unique_ssh_ports(self, local_provider):
        """Test that multiple tasks get unique SSH ports."""
        tasks = []
        ports_used = set()

        # Create multiple tasks
        for i in range(3):
            config = TaskConfig(
                name=f"local-ssh-test-{i}",
                instance_type="a100",
                command=["echo", f"task {i}"]
            )
            task = local_provider.submit_task(
                instance_type="a100",
                config=config
            )
            tasks.append(task)
            ports_used.add(task.ssh_port)

        # Verify all ports are unique
        assert len(ports_used) == 3

        # Verify ports are in expected range
        for port in ports_used:
            assert 22000 <= port < 23000

    def test_ssh_fields_persist_after_task_retrieval(self, local_provider):
        """Test that SSH fields are maintained when retrieving a task."""
        config = TaskConfig(
            name="persistent-ssh-test",
            instance_type="a100",
            command=["sleep", "1"]
        )

        # Submit task
        task = local_provider.submit_task(
            instance_type="a100",
            config=config
        )
        original_ssh_host = task.ssh_host
        original_ssh_port = task.ssh_port
        original_ssh_user = task.ssh_user

        # Retrieve task by ID
        retrieved_task = local_provider.get_task(task.task_id)

        # Verify SSH fields match
        assert retrieved_task.ssh_host == original_ssh_host
        assert retrieved_task.ssh_port == original_ssh_port
        assert retrieved_task.ssh_user == original_ssh_user

    def test_local_provider_ssh_integration_with_flow(self, local_config):
        """Test SSH fields through the Flow interface with local provider."""
        flow = Flow(config=local_config)

        # Submit a task through Flow
        config = TaskConfig(
            name="flow-ssh-test",
            instance_type="a100",
            command=["python", "-c", "print('SSH integration test')"]
        )
        task = flow.run(config)

        # Verify SSH fields are properly set
        assert task.ssh_host == "localhost"
        assert isinstance(task.ssh_port, int)
        assert task.ssh_user == "flow"

        # Note: We don't actually test SSH connection here as that would
        # require subprocess calls. The E2E tests handle actual connections.

    def test_task_ssh_fields_match_provider_pattern(self, local_provider):
        """Test that SSH fields follow expected patterns for local provider."""
        config = TaskConfig(
            name="pattern-test",
            instance_type="a100",
            command=["echo", "test patterns"]
        )

        task = local_provider.submit_task(
            instance_type="a100",
            config=config
        )

        # Local provider specific patterns
        assert task.ssh_host == "localhost"
        assert task.ssh_user == "flow"
        # Port should be 22000 + task index
        assert task.ssh_port == 22000 + len(local_provider.tasks) - 1

    def test_ssh_fields_available_immediately(self, local_provider):
        """Test that SSH fields are available immediately after task creation."""
        config = TaskConfig(
            name="immediate-ssh-test",
            instance_type="a100",
            command=["echo", "immediate"]
        )

        task = local_provider.submit_task(
            instance_type="a100",
            config=config
        )

        # SSH fields should be available immediately, not just after RUNNING
        assert task.ssh_host is not None
        assert task.ssh_port is not None
        assert task.ssh_user is not None

        # This is important for users who want to set up SSH tunnels early
