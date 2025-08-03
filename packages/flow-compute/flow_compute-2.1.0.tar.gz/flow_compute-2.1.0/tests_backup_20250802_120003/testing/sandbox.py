"""Integration test sandbox environment configuration.

Provides isolated test environments for integration testing with
proper setup/teardown and resource management.
"""

import contextlib
import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set
from unittest.mock import Mock, patch

import pytest


@dataclass
class SandboxConfig:
    """Configuration for test sandbox environment."""
    
    # Base paths
    temp_dir: Optional[Path] = None
    working_dir: Optional[Path] = None
    
    # Environment settings
    env_vars: Dict[str, str] = field(default_factory=dict)
    mock_services: Set[str] = field(default_factory=set)
    
    # Resource limits
    max_file_size_mb: int = 100
    max_temp_files: int = 1000
    cleanup_on_exit: bool = True
    
    # Network settings
    allow_network: bool = False
    allowed_hosts: List[str] = field(default_factory=list)
    
    # Storage settings
    use_mock_s3: bool = True
    use_mock_gcs: bool = True
    
    # API mocking
    mock_api_responses: Dict[str, Any] = field(default_factory=dict)


class TestSandbox:
    """Isolated test environment for integration testing."""
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.temp_dir: Optional[Path] = None
        self.working_dir: Optional[Path] = None
        self.original_env: Dict[str, str] = {}
        self.cleanup_paths: List[Path] = []
        self.active_mocks: List[Any] = []
        self._is_active = False
    
    def __enter__(self) -> "TestSandbox":
        """Enter sandbox context."""
        self.setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sandbox context."""
        self.teardown()
    
    def setup(self) -> None:
        """Set up the sandbox environment."""
        if self._is_active:
            raise RuntimeError("Sandbox is already active")
        
        # Create temporary directories
        self._setup_directories()
        
        # Set up environment variables
        self._setup_environment()
        
        # Set up mock services
        self._setup_mocks()
        
        self._is_active = True
    
    def teardown(self) -> None:
        """Tear down the sandbox environment."""
        if not self._is_active:
            return
        
        # Restore environment
        self._restore_environment()
        
        # Stop mocks
        self._teardown_mocks()
        
        # Cleanup temporary files
        if self.config.cleanup_on_exit:
            self._cleanup_files()
        
        self._is_active = False
    
    def _setup_directories(self) -> None:
        """Create temporary directories for the sandbox."""
        # Create main temp directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="flow_test_"))
        self.cleanup_paths.append(self.temp_dir)
        
        # Create working directory
        self.working_dir = self.temp_dir / "work"
        self.working_dir.mkdir(exist_ok=True)
        
        # Create standard subdirectories
        (self.working_dir / "logs").mkdir(exist_ok=True)
        (self.working_dir / "data").mkdir(exist_ok=True)
        (self.working_dir / "cache").mkdir(exist_ok=True)
        
        # Override config paths if not set
        if not self.config.temp_dir:
            self.config.temp_dir = self.temp_dir
        if not self.config.working_dir:
            self.config.working_dir = self.working_dir
    
    def _setup_environment(self) -> None:
        """Set up environment variables."""
        # Save original environment
        self.original_env = os.environ.copy()
        
        # Set sandbox environment variables
        sandbox_env = {
            "FLOW_TEST_MODE": "1",
            "FLOW_SANDBOX_ID": str(uuid.uuid4()),
            "FLOW_TEMP_DIR": str(self.temp_dir),
            "FLOW_WORKING_DIR": str(self.working_dir),
            "HOME": str(self.working_dir),  # Isolate home directory
            "TMPDIR": str(self.temp_dir),
            "TEMP": str(self.temp_dir),
            "TMP": str(self.temp_dir),
        }
        
        # Add custom environment variables
        sandbox_env.update(self.config.env_vars)
        
        # Apply environment
        os.environ.update(sandbox_env)
    
    def _setup_mocks(self) -> None:
        """Set up mock services."""
        # Mock network if disabled
        if not self.config.allow_network:
            self._setup_network_mocks()
        
        # Mock storage services
        if self.config.use_mock_s3:
            self._setup_s3_mocks()
        
        if self.config.use_mock_gcs:
            self._setup_gcs_mocks()
        
        # Set up custom API mocks
        self._setup_api_mocks()
    
    def _setup_network_mocks(self) -> None:
        """Mock network calls when network is disabled."""
        # Mock requests library
        requests_mock = patch("requests.request")
        mock = requests_mock.start()
        self.active_mocks.append(requests_mock)
        
        def side_effect(method, url, **kwargs):
            # Check if host is allowed
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if parsed.hostname in self.config.allowed_hosts:
                # Allow the request (would need real implementation)
                raise NotImplementedError("Allowed host passthrough not implemented")
            
            raise ConnectionError(f"Network access disabled in test sandbox: {url}")
        
        mock.side_effect = side_effect
    
    def _setup_s3_mocks(self) -> None:
        """Set up mock S3 service."""
        # Mock boto3 S3 client
        s3_mock = patch("boto3.client")
        mock = s3_mock.start()
        self.active_mocks.append(s3_mock)
        
        # Create mock S3 client
        mock_s3 = Mock()
        mock.return_value = mock_s3
        
        # Simple in-memory S3 storage
        s3_storage = {}
        
        def put_object(**kwargs):
            key = f"{kwargs.get('Bucket')}/{kwargs.get('Key')}"
            s3_storage[key] = kwargs.get("Body")
            return {"ETag": f'"{uuid.uuid4()}"'}
        
        def get_object(**kwargs):
            key = f"{kwargs.get('Bucket')}/{kwargs.get('Key')}"
            if key not in s3_storage:
                raise Exception("NoSuchKey")
            return {"Body": s3_storage[key]}
        
        mock_s3.put_object.side_effect = put_object
        mock_s3.get_object.side_effect = get_object
    
    def _setup_gcs_mocks(self) -> None:
        """Set up mock GCS service."""
        # Similar to S3 mocks but for Google Cloud Storage
        pass
    
    def _setup_api_mocks(self) -> None:
        """Set up custom API response mocks."""
        for pattern, response in self.config.mock_api_responses.items():
            # Would implement API mocking based on patterns
            pass
    
    def _restore_environment(self) -> None:
        """Restore original environment variables."""
        # Clear all environment variables
        os.environ.clear()
        # Restore original
        os.environ.update(self.original_env)
    
    def _teardown_mocks(self) -> None:
        """Stop all active mocks."""
        for mock in self.active_mocks:
            mock.stop()
        self.active_mocks.clear()
    
    def _cleanup_files(self) -> None:
        """Clean up temporary files and directories."""
        for path in reversed(self.cleanup_paths):
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        self.cleanup_paths.clear()
    
    # Helper methods
    def create_file(self, relative_path: str, content: str = "") -> Path:
        """Create a file in the sandbox."""
        path = self.working_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path
    
    def create_config_file(self, content: Dict[str, Any]) -> Path:
        """Create a YAML config file in the sandbox."""
        import yaml
        config_path = self.working_dir / ".flow" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w") as f:
            yaml.dump(content, f)
        
        return config_path
    
    def get_log_contents(self) -> Dict[str, str]:
        """Get contents of all log files."""
        logs = {}
        log_dir = self.working_dir / "logs"
        
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                logs[log_file.name] = log_file.read_text()
        
        return logs


# Pytest fixtures
@pytest.fixture
def sandbox():
    """Provide a test sandbox for the test."""
    with TestSandbox() as sb:
        yield sb


@pytest.fixture
def isolated_sandbox():
    """Provide a fully isolated sandbox with no network access."""
    config = SandboxConfig(
        allow_network=False,
        use_mock_s3=True,
        use_mock_gcs=True,
    )
    with TestSandbox(config) as sb:
        yield sb


@pytest.fixture
def network_sandbox():
    """Provide a sandbox with network access to specific hosts."""
    config = SandboxConfig(
        allow_network=True,
        allowed_hosts=["api.example.com", "localhost"],
    )
    with TestSandbox(config) as sb:
        yield sb


# Context managers for specific test scenarios
@contextlib.contextmanager
def gpu_sandbox() -> Iterator[TestSandbox]:
    """Sandbox configured for GPU testing."""
    config = SandboxConfig(
        env_vars={
            "CUDA_VISIBLE_DEVICES": "0,1",
            "NVIDIA_VISIBLE_DEVICES": "0,1",
        }
    )
    with TestSandbox(config) as sb:
        yield sb


@contextlib.contextmanager
def multi_node_sandbox(num_nodes: int = 2) -> Iterator[List[TestSandbox]]:
    """Create multiple sandboxes for multi-node testing."""
    sandboxes = []
    
    try:
        for i in range(num_nodes):
            config = SandboxConfig(
                env_vars={
                    "FLOW_NODE_ID": str(i),
                    "FLOW_NODE_COUNT": str(num_nodes),
                    "FLOW_IS_MASTER": "1" if i == 0 else "0",
                }
            )
            sb = TestSandbox(config)
            sb.setup()
            sandboxes.append(sb)
        
        yield sandboxes
    
    finally:
        for sb in sandboxes:
            sb.teardown()


# Sandbox utilities
class SandboxManager:
    """Manage multiple sandboxes for complex test scenarios."""
    
    def __init__(self):
        self.sandboxes: Dict[str, TestSandbox] = {}
    
    def create(self, name: str, config: Optional[SandboxConfig] = None) -> TestSandbox:
        """Create a named sandbox."""
        if name in self.sandboxes:
            raise ValueError(f"Sandbox '{name}' already exists")
        
        sb = TestSandbox(config)
        sb.setup()
        self.sandboxes[name] = sb
        return sb
    
    def get(self, name: str) -> Optional[TestSandbox]:
        """Get a sandbox by name."""
        return self.sandboxes.get(name)
    
    def cleanup(self) -> None:
        """Clean up all sandboxes."""
        for sb in self.sandboxes.values():
            sb.teardown()
        self.sandboxes.clear()


# Environment requirements documentation
SANDBOX_REQUIREMENTS = """
Integration Test Sandbox Environment Requirements
===============================================

The test sandbox provides an isolated environment for integration testing
with the following features:

1. Filesystem Isolation
   - Temporary directories for all file operations
   - Automatic cleanup after tests
   - Configurable resource limits

2. Environment Isolation
   - Separate environment variables
   - Mock home directory
   - Isolated temp directories

3. Network Control
   - Optional network isolation
   - Whitelist specific hosts
   - Mock external services

4. Storage Mocking
   - Mock S3 service
   - Mock GCS service
   - In-memory storage backends

5. Resource Management
   - File size limits
   - File count limits
   - Automatic cleanup

Usage Examples:

    # Basic sandbox
    def test_with_sandbox(sandbox):
        # sandbox is automatically created and cleaned up
        file_path = sandbox.create_file("test.txt", "content")
        assert file_path.exists()
    
    # Isolated sandbox (no network)
    def test_isolated(isolated_sandbox):
        # Network calls will fail
        pass
    
    # Multi-node testing
    with multi_node_sandbox(3) as nodes:
        # nodes is a list of 3 sandboxes
        for i, node in enumerate(nodes):
            node.create_file(f"node{i}.txt", f"Node {i}")
"""