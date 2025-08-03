"""Environment fixtures for Flow SDK tests."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from flow import Flow
from flow.api.models import StorageInterface, Task, TaskStatus, Volume
from flow.providers.fcp.core.models import FCPBid


@pytest.fixture
def mock_fcp_environment(tmp_path, monkeypatch):
    """Complete FCP API mock environment.
    
    Provides a fully mocked FCP environment with:
    - Mock API responses
    - Test credentials
    - Isolated file system
    - Deterministic behavior
    """
    # Set up test environment variables
    monkeypatch.setenv("FCP_API_KEY", "test-api-key-123")
    monkeypatch.setenv("FCP_API_URL", "https://api.test.foundationcloud.io")
    monkeypatch.setenv("FLOW_CONFIG_DIR", str(tmp_path / ".flow"))
    monkeypatch.setenv("FLOW_CACHE_DIR", str(tmp_path / ".cache"))

    # Create config directories
    (tmp_path / ".flow").mkdir(exist_ok=True)
    (tmp_path / ".cache").mkdir(exist_ok=True)

    # Mock API client
    with patch('flow.providers.fcp.provider.FCPClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Set up default responses
        mock_client.get_current_user.return_value = {
            "id": "user-123",
            "email": "test@example.com",
            "organization_id": "org-123"
        }

        mock_client.get_project.return_value = {
            "id": "project-123",
            "name": "test-project",
            "organization_id": "org-123"
        }

        yield {
            "client": mock_client,
            "tmp_path": tmp_path,
            "api_key": "test-api-key-123",
            "user_id": "user-123",
            "project_id": "project-123"
        }


@pytest.fixture
def authenticated_flow(mock_fcp_environment):
    """Pre-authenticated Flow instance ready for testing.
    
    Returns a Flow instance that:
    - Has valid authentication
    - Uses mock FCP client
    - Is isolated from system config
    """
    from flow._internal.config import Config
    config = Config(
        auth_token=mock_fcp_environment["api_key"],
        api_url="https://api.test.foundationcloud.io",
        project="test-project",
        provider="fcp"
    )
    flow = Flow(config=config)
    return flow


@pytest.fixture
def sample_task():
    """Sample Task object for testing."""
    return Task(
        task_id="task-123",
        name="test-training",
        status=TaskStatus.RUNNING,
        created_at=datetime.now(),
        instance_type="a100.80gb.sxm4.1x",
        num_instances=1,
        region="us-central1-a",
        cost_per_hour="$25.60",
        ssh_host="1.2.3.4",
        ssh_port=22,
        ssh_user="ubuntu",
        _provider=None  # Mock provider
    )


@pytest.fixture
def sample_volume():
    """Sample Volume object for testing."""
    return Volume(
        volume_id="vol-123",
        name="training-data",
        size_gb=100,
        region="us-central1-a",
        interface=StorageInterface.BLOCK,
        created_at=datetime.now()
    )


@pytest.fixture
def sample_bid_response():
    """Sample bid response for testing."""
    return FCPBid(
        bid_id="bid-123",
        status="SCHEDULED",
        instance_type="a100.80gb.sxm4.1x",
        gpu_count=1,
        gpu_memory_gb=80,
        cpu_count=24,
        memory_gb=256,
        price_per_hour="$25.60",
        ssh_host="1.2.3.4",
        ssh_port=22,
        ssh_user="ubuntu",
        estimated_cost="$12.80",
        estimated_start_time="2024-01-01T12:00:00Z",
        volumes=["vol-123"]
    )


@pytest.fixture
def mock_api_responses():
    """Load versioned mock API responses.
    
    Returns a dictionary of endpoint -> response mappings
    for the current API version.
    """
    responses_dir = Path(__file__).parent.parent / "data" / "api" / "v2024-01-01"
    responses = {}

    # Load each JSON file in the responses directory
    if responses_dir.exists():
        for json_file in responses_dir.glob("*.json"):
            endpoint = json_file.stem
            with open(json_file) as f:
                responses[endpoint] = json.load(f)

    # Provide defaults if files don't exist yet
    if not responses:
        responses = {
            "submit_task": {
                "bid_id": "bid-123",
                "status": "pending",
                "message": "Task submitted successfully"
            },
            "get_bid": {
                "bid_id": "bid-123",
                "status": "scheduled",
                "instance_type": "a100.80gb.sxm4.1x",
                "ssh_host": "1.2.3.4",
                "ssh_port": 22
            },
            "list_bids": {
                "bids": [
                    {"bid_id": "bid-123", "status": "running"},
                    {"bid_id": "bid-124", "status": "completed"}
                ]
            }
        }

    return responses


@pytest.fixture(autouse=True)
def isolated_test_environment(tmp_path, monkeypatch):
    """Ensure each test runs in complete isolation.
    
    Automatically applied to all tests to:
    - Isolate file system operations
    - Clear global state
    - Prevent test interference
    """
    # Set isolated paths
    monkeypatch.setenv("FLOW_CONFIG_DIR", str(tmp_path / ".flow"))
    monkeypatch.setenv("FLOW_CACHE_DIR", str(tmp_path / ".cache"))
    monkeypatch.setenv("HOME", str(tmp_path))

    # Clear any global Flow instance
    if hasattr(Flow, '_instance'):
        Flow._instance = None

    yield

    # Cleanup is automatic with tmp_path
