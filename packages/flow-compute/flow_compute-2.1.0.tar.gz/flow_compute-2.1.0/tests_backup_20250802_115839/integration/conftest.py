"""Common fixtures for integration tests.

This module provides reusable fixtures for integration tests to ensure
consistent mock setup and reduce code duplication.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from flow._internal.config import Config
from flow.api.models import Task, TaskStatus, Volume, StorageInterface
from flow.providers.fcp.core.models import FCPInstance, FCPBid


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client for API interactions."""
    client = Mock()
    client.request = MagicMock()
    client.base_url = "https://api.mlfoundry.com"
    return client


@pytest.fixture
def mock_config():
    """Create a mock Flow configuration."""
    return Config(
        provider="fcp",
        auth_token="test-token",
        provider_config={
            "api_url": "https://api.test.com",
            "project": "test-project"
        }
    )


@pytest.fixture
def sample_task():
    """Create a sample task for testing."""
    return Task(
        task_id="test-123",
        name="test-task",
        status=TaskStatus.RUNNING,
        created_at=datetime.now(timezone.utc),
        instance_type="gpu.a100",
        num_instances=1,
        region="us-central1",
        cost_per_hour="$10.00",
        ssh_host="1.2.3.4",
        ssh_port=22
    )


@pytest.fixture
def sample_tasks():
    """Create a list of sample tasks."""
    tasks = []
    for i in range(5):
        task = Task(
            task_id=f"task-{i}",
            name=f"test-task-{i}",
            status=TaskStatus.RUNNING if i % 2 == 0 else TaskStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
            instance_type="gpu.a100" if i % 3 == 0 else "cpu.large",
            num_instances=1,
            region="us-central1",
            cost_per_hour=f"${i * 2 + 1}.00"
        )
        tasks.append(task)
    return tasks


@pytest.fixture
def sample_volume():
    """Create a sample volume for testing."""
    return Volume(
        volume_id="vol_abc123",
        name="test-volume",
        size_gb=100,
        region="us-east-1",
        interface=StorageInterface.BLOCK,
        created_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_volumes():
    """Create a list of sample volumes."""
    volumes = []
    for i in range(3):
        volume = Volume(
            volume_id=f"vol_{i:03d}",
            name=f"volume-{i}",
            size_gb=100 * (i + 1),
            region="us-east-1",
            interface=StorageInterface.BLOCK,
            created_at=datetime.now(timezone.utc)
        )
        volumes.append(volume)
    return volumes


@pytest.fixture
def mock_fcp_instance():
    """Create a mock FCP instance."""
    return FCPInstance(
        id="inst-123",
        bid_id="bid-123",
        status="running",
        public_ip="1.2.3.4",
        private_ip="10.0.0.1",
        ssh_port=22,
        ssh_user="ubuntu",
        region="us-central1",
        created_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_fcp_bid():
    """Create a mock FCP bid."""
    return FCPBid(
        fid="bid-123",
        name="test-task",
        status="running",
        limit_price="$10.00",
        created_at=datetime.now(timezone.utc),
        project="proj-123",
        created_by="user-123",
        instance_quantity=1,
        instance_type="it_gpu_a100",
        region="us-central1",
        instances=["inst-123"]
    )


@pytest.fixture
def mock_ssh_key_manager(mock_http_client):
    """Create a mock SSH key manager."""
    from flow.providers.fcp.resources.ssh import SSHKeyManager
    manager = SSHKeyManager(http_client=mock_http_client, project_id="test-project")
    manager.ensure_keys = Mock(return_value=["key-123"])
    manager.list_keys = Mock(return_value=[])
    return manager


@pytest.fixture
def mock_flow_client(mock_config, mock_http_client):
    """Create a mock Flow client."""
    from flow import Flow
    flow_client = Mock(spec=Flow)
    flow_client.config = mock_config
    flow_client.list_tasks = Mock(return_value=[])
    flow_client.list_volumes = Mock(return_value=[])
    flow_client.get_task = Mock()
    flow_client.create_volume = Mock()
    flow_client.delete_volume = Mock()
    return flow_client


@pytest.fixture
def mock_provider(mock_config, mock_http_client):
    """Create a mock FCP provider."""
    from flow.providers.fcp.provider import FCPProvider
    provider = FCPProvider(mock_config, mock_http_client)
    provider._project_id = "test-project-id"
    provider._get_project_id = Mock(return_value="test-project-id")
    return provider


@pytest.fixture
def mock_remote_operations():
    """Create mock remote operations."""
    from flow.providers.fcp.remote_operations import FCPRemoteOperations
    ops = Mock(spec=FCPRemoteOperations)
    ops.execute_command = Mock(return_value="command output")
    ops.upload_file = Mock()
    ops.download_file = Mock()
    return ops


@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def mock_flow_init():
    """Mock Flow initialization for CLI tests."""
    import contextlib
    from unittest.mock import patch
    
    @contextlib.contextmanager
    def _mock_flow_init():
        with patch('flow.Flow._load_config'), \
             patch('flow.Flow._ensure_provider'), \
             patch('flow._internal.config_loader.ConfigLoader.load_config'):
            yield
    
    return _mock_flow_init


# Helper functions for common test scenarios

def create_mock_api_response(data: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create a standardized API response."""
    return {
        "data": data,
        "status_code": status_code
    }


def create_mock_task_response(task_id: str, status: str = "running", 
                            instances: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a mock task/bid response."""
    return {
        "id": task_id,
        "status": status,
        "instances": instances or [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "instance_type": "it_gpu_a100",
        "region": "us-central1"
    }


def create_mock_instance_response(instance_id: str, public_ip: Optional[str] = None) -> Dict[str, Any]:
    """Create a mock instance response."""
    response = {
        "id": instance_id,
        "status": "running",
        "private_ip": "10.0.0.1",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if public_ip:
        response["public_ip"] = public_ip
    return response