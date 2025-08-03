"""Pytest configuration and shared fixtures."""
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, Mock, patch

import pytest
from pytest import MonkeyPatch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# No global environment defaults - each test should set what it needs
# This ensures proper test isolation and explicit dependencies

# Disable keychain access during tests to prevent authentication prompts
os.environ["FLOW_DISABLE_KEYCHAIN"] = "1"

# Enable default instance type mappings for tests
os.environ["FCP_INCLUDE_DEFAULT_MAPPINGS"] = "true"

# Fixture to handle lazy app initialization for tests
@pytest.fixture
def flow_app():
    """Get Flow app instance for testing."""
    # Import here to avoid early initialization
    from flow import app
    # Force initialization with test config
    if callable(app):
        return app()
    return app

# Import our enhanced fixtures
from tests.support.fixtures.environment import sample_volume


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests (E2E tests with real GPU instances)"
    )
    parser.addoption(
        "--keep-instances",
        action="store_true",
        default=False,
        help="Keep test instances running after tests complete"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (10+ minutes, real GPU instances)"
    )
    config.addinivalue_line(
        "markers",
        "e2e: marks tests as end-to-end (requires real infrastructure)"
    )
    config.addinivalue_line(
        "markers", 
        "network: marks tests that require network access"
    )
    config.addinivalue_line(
        "markers",
        "gpu: marks tests that require GPU hardware"
    )
    config.addinivalue_line(
        "markers",
        "distributed: marks tests for distributed/multi-node scenarios"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers and auto-categorize tests."""
    
    # Auto-mark based on directory structure
    for item in items:
        test_path = Path(item.fspath)
        
        # Mark based on directory
        if "unit" in test_path.parts:
            item.add_marker(pytest.mark.unit)
        elif "integration" in test_path.parts:
            item.add_marker(pytest.mark.integration)
        elif "e2e" in test_path.parts:
            item.add_marker(pytest.mark.e2e)
        
        # Mark based on test name patterns
        test_name = item.name.lower()
        
        if "benchmark" in test_name or "perf" in test_name:
            item.add_marker(pytest.mark.benchmark)
            item.add_marker(pytest.mark.slow)
        
        if "network" in test_name or "http" in test_name or "api" in test_name:
            item.add_marker(pytest.mark.network)
        
        if "gpu" in test_name or "cuda" in test_name:
            item.add_marker(pytest.mark.gpu)
        
        if "multi_node" in test_name or "distributed" in test_name:
            item.add_marker(pytest.mark.distributed)
    
    # Skip slow tests unless --run-slow is passed
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


# Test configuration helpers following YAGNI principle
def create_mock_config(provider="fcp", **attrs):
    """Create a mock Config object for unit tests. No magic, just what we need."""
    config = MagicMock()
    config.provider = provider
    config.auth_token = attrs.get("auth_token", "test-token")

    # Provider config dict matches Config.provider_config structure
    config.provider_config = {}

    if provider == "fcp":
        config.provider_config = {
            "api_url": attrs.get("api_url", "https://api.mlfoundry.com"),
            "project": attrs.get("project", "test-project"),
            "region": attrs.get("region", "us-central1-a")
        }

    # Add get_headers method
    config.get_headers.return_value = {
        "Authorization": f"Bearer {config.auth_token}",
        "Content-Type": "application/json"
    }

    return config


@contextmanager
def test_config_context(provider="fcp", auth_token="test-token", project="test-project"):
    """For integration tests that need a real Config object."""
    env_vars = {
        "FLOW_PROVIDER": provider,
        "FCP_API_KEY": auth_token,
        "FCP_DEFAULT_PROJECT": project,
        "FCP_DEFAULT_REGION": "us-central1-a"
    }

    with patch.dict(os.environ, env_vars, clear=True):
        from flow._internal.config import Config
        yield Config.from_env(require_auth=True)




@pytest.fixture
def mock_env(monkeypatch: MonkeyPatch) -> Generator[Dict[str, str], None, None]:
    """Mock environment variables for testing."""
    env_vars = {
        "FCP_API_KEY": "test-api-key",
        "FCP_API_URL": "https://api.test.com",
        "FCP_DEFAULT_PROJECT": "test-project",
        "FCP_DEFAULT_REGION": "us-east-1",
        "FLOW_PROVIDER": "fcp"
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    yield env_vars


@pytest.fixture
def mock_http_client() -> Mock:
    """Mock HTTP client for testing."""
    client = Mock()
    client.request = MagicMock()
    client.get = MagicMock()
    client.post = MagicMock()
    client.put = MagicMock()
    client.delete = MagicMock()
    return client


@pytest.fixture
def sample_task_config() -> Dict[str, Any]:
    """Sample task configuration for testing."""
    return {
        "instance_type": "a100.80gb.sxm4.1x",
        "command": ["python", "train.py"],
        "environment": {"MODEL": "gpt-3"},
        "working_directory": "/workspace",
        "volumes": [
            {
                "name": "data",
                "mount_path": "/data"
            }
        ],
        "ssh_keys": ["ssh-key-1"],
        "ports": [8080, 8081],
        "tags": {"team": "ml", "project": "training"}
    }


@pytest.fixture
def sample_instance() -> Dict[str, Any]:
    """Sample instance data for testing."""
    return {
        "instance_id": "i-1234567890",
        "instance_type": "a100.80gb.sxm4.1x",
        "status": "running",
        "region": "us-east-1",
        "public_ip": "1.2.3.4",
        "private_ip": "10.0.0.1",
        "ssh_host": "1.2.3.4",
        "ssh_port": 22,
        "created_at": "2024-01-01T00:00:00Z",
        "volumes": ["vol-123"],
        "tags": {"team": "ml"}
    }


@pytest.fixture
def sample_volume() -> Dict[str, Any]:
    """Sample volume data for testing."""
    return {
        "volume_id": "vol-123",
        "name": "data-volume",
        "size_gb": 100,
        "status": "available",
        "region": "us-east-1",
        "created_at": "2024-01-01T00:00:00Z",
        "attached_to": None,
        "mount_path": "/data"
    }


@pytest.fixture(scope="session")
def flow_config():
    """Shared config for tests - created once per session."""
    from flow._internal.config import Config
    return Config(
        provider="fcp",
        auth_token="test-token",
        provider_config={"project_id": "test-project"}
    )


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment for each test."""
    # Remove Flow-related env vars
    env_backup = {}
    for key in list(os.environ.keys()):
        if key.startswith('FLOW_') or key.startswith('FCP_'):
            env_backup[key] = os.environ.get(key)
            monkeypatch.delenv(key, raising=False)

    yield monkeypatch

    # Restore environment after test
    for key, value in env_backup.items():
        if value is not None:
            os.environ[key] = value
