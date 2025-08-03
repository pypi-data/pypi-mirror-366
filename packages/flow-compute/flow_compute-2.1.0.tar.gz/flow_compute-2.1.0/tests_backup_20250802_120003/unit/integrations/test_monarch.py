"""
Unit tests for Monarch-Flow integration.

Tests the core abstractions and Flow implementation following SOLID principles.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from flow._internal.integrations.monarch import (
    ComputeRequirements,
    ProcessHandle,
    ProcessLifecycleEvents,
    ComputeAllocator,
    FlowComputeAllocator,
    ComputeAllocatorFactory,
    MonarchFlowConfig,
    MonarchFlowError,
    AllocationError,
)
from flow.api.models import Task, TaskConfig


class TestComputeRequirements:
    """Test the ComputeRequirements data class."""
    
    def test_basic_requirements(self):
        """Test creating basic compute requirements."""
        req = ComputeRequirements(gpu_count=4)
        assert req.gpu_count == 4
        assert req.gpu_memory_gb is None
        assert req.gpu_type is None
    
    def test_full_requirements(self):
        """Test creating requirements with all fields."""
        req = ComputeRequirements(
            gpu_count=8,
            gpu_memory_gb=80,
            gpu_type="h100",
            cpu_count=64,
            memory_gb=512,
            region="us-west-2"
        )
        assert req.gpu_count == 8
        assert req.gpu_memory_gb == 80
        assert req.gpu_type == "h100"
        assert req.cpu_count == 64
        assert req.memory_gb == 512
        assert req.region == "us-west-2"


class TestProcessHandle:
    """Test the ProcessHandle data class."""
    
    def test_process_handle(self):
        """Test creating a process handle."""
        handle = ProcessHandle(
            id="task-123",
            address="10.0.0.1:8000",
            metadata={"provider": "fcp", "gpu_count": 2}
        )
        assert handle.id == "task-123"
        assert handle.address == "10.0.0.1:8000"
        assert handle.metadata["provider"] == "fcp"
        assert handle.metadata["gpu_count"] == 2


class TestProcessLifecycleEvents:
    """Test the ProcessLifecycleEvents protocol."""
    
    def test_protocol_implementation(self):
        """Test that a class can implement the protocol."""
        
        class MyLifecycle:
            async def on_created(self, handle: ProcessHandle) -> None:
                pass
            
            async def on_running(self, handle: ProcessHandle) -> None:
                pass
            
            async def on_stopped(self, handle: ProcessHandle, reason: str) -> None:
                pass
            
            async def on_failed(self, handle: ProcessHandle, error: str) -> None:
                pass
        
        # Should be able to use as ProcessLifecycleEvents
        lifecycle: ProcessLifecycleEvents = MyLifecycle()
        assert hasattr(lifecycle, "on_created")
        assert hasattr(lifecycle, "on_running")
        assert hasattr(lifecycle, "on_stopped")
        assert hasattr(lifecycle, "on_failed")


class TestFlowComputeAllocator:
    """Test the Flow implementation of ComputeAllocator."""
    
    @pytest.fixture
    def mock_flow(self):
        """Create a mock Flow client."""
        flow = Mock()
        flow.run = AsyncMock()
        return flow
    
    @pytest.fixture
    def mock_task(self):
        """Create a mock Task."""
        task = Mock(spec=Task)
        task.task_id = "task-123"
        task.status = "pending"
        task.ssh_host = "10.0.0.1"
        task.instance_type = "a100"
        task.region = "us-west-2"
        task.stop = AsyncMock()
        task.refresh = Mock()
        return task
    
    @pytest.fixture
    def allocator(self, mock_flow):
        """Create a FlowComputeAllocator instance."""
        return FlowComputeAllocator(flow_client=mock_flow)
    
    @pytest.mark.asyncio
    async def test_allocate_basic(self, allocator, mock_flow, mock_task):
        """Test basic allocation."""
        mock_flow.run.return_value = mock_task
        
        # Create mock lifecycle
        lifecycle = AsyncMock(spec=ProcessLifecycleEvents)
        
        # Allocate
        requirements = ComputeRequirements(gpu_count=2, gpu_type="a100")
        handle = await allocator.allocate(requirements, lifecycle)
        
        # Verify handle
        assert handle.id == "task-123"
        assert handle.address == "10.0.0.1:8000"
        assert handle.metadata["gpu_count"] == 2
        
        # Verify Flow was called correctly
        mock_flow.run.assert_called_once()
        config = mock_flow.run.call_args[0][0]
        assert isinstance(config, TaskConfig)
        assert config.instance_type == "2xa100"
        assert config.name == "monarch-worker-2gpu"
        
        # Verify lifecycle was notified
        lifecycle.on_created.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_allocate_with_capabilities(self, allocator, mock_flow, mock_task):
        """Test allocation with capability-based requirements."""
        mock_flow.run.return_value = mock_task
        
        lifecycle = AsyncMock(spec=ProcessLifecycleEvents)
        
        # Allocate with capabilities
        requirements = ComputeRequirements(
            gpu_count=4,
            gpu_memory_gb=80,
            cpu_count=32,
            memory_gb=256
        )
        handle = await allocator.allocate(requirements, lifecycle)
        
        # Verify config
        config = mock_flow.run.call_args[0][0]
        # With 4 GPUs and memory requirement, it should use instance type
        assert config.instance_type == "4xa100"
        # min_gpu_memory_gb should not be set when using instance_type
        assert config.min_gpu_memory_gb is None
    
    @pytest.mark.asyncio
    async def test_deallocate(self, allocator, mock_flow, mock_task):
        """Test deallocation."""
        mock_flow.run.return_value = mock_task
        
        # First allocate
        lifecycle = AsyncMock(spec=ProcessLifecycleEvents)
        requirements = ComputeRequirements(gpu_count=1)
        handle = await allocator.allocate(requirements, lifecycle)
        
        # Then deallocate
        await allocator.deallocate(handle)
        
        # Verify task was stopped
        mock_task.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check(self, allocator, mock_flow, mock_task):
        """Test health checking."""
        mock_flow.run.return_value = mock_task
        
        # Allocate
        lifecycle = AsyncMock(spec=ProcessLifecycleEvents)
        requirements = ComputeRequirements(gpu_count=1)
        handle = await allocator.allocate(requirements, lifecycle)
        
        # Check health when running
        mock_task.status = "running"
        assert await allocator.health_check(handle) is True
        
        # Check health when stopped
        mock_task.status = "stopped"
        assert await allocator.health_check(handle) is False
        
        # Check health for unknown handle
        unknown_handle = ProcessHandle("unknown", "nowhere", {})
        assert await allocator.health_check(unknown_handle) is False
    
    @pytest.mark.asyncio
    async def test_lifecycle_monitoring(self, allocator, mock_flow, mock_task):
        """Test that lifecycle events are properly monitored."""
        mock_flow.run.return_value = mock_task
        
        # Track lifecycle calls
        lifecycle_calls = []
        
        class TestLifecycle:
            """Test implementation of ProcessLifecycleEvents protocol."""
            
            async def on_created(self, handle):
                lifecycle_calls.append(("created", handle.id))
            
            async def on_running(self, handle):
                lifecycle_calls.append(("running", handle.id))
            
            async def on_stopped(self, handle, reason):
                lifecycle_calls.append(("stopped", handle.id, reason))
            
            async def on_failed(self, handle, error):
                lifecycle_calls.append(("failed", handle.id, error))
        
        lifecycle = TestLifecycle()
        
        # Allocate
        requirements = ComputeRequirements(gpu_count=1)
        handle = await allocator.allocate(requirements, lifecycle)
        
        # Simulate task becoming running
        mock_task.status = "running"
        await asyncio.sleep(0.1)  # Let monitor run
        
        # Check lifecycle was called
        assert ("created", "task-123") in lifecycle_calls


class TestComputeAllocatorFactory:
    """Test the factory pattern for creating allocators."""
    
    def test_register_and_create(self):
        """Test registering and creating allocators."""
        # Clear any existing registrations
        ComputeAllocatorFactory._creators.clear()
        
        # Register a mock allocator
        class MockAllocator:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
        
        ComputeAllocatorFactory.register("mock", MockAllocator)
        
        # Create an instance
        allocator = ComputeAllocatorFactory.create("mock", foo="bar")
        assert isinstance(allocator, MockAllocator)
        assert allocator.kwargs["foo"] == "bar"
    
    def test_create_unknown_allocator(self):
        """Test creating an unknown allocator type."""
        with pytest.raises(ValueError, match="Unknown allocator: nonexistent"):
            ComputeAllocatorFactory.create("nonexistent")
    
    def test_flow_allocator_registered(self):
        """Test that FlowComputeAllocator is pre-registered."""
        # Re-register Flow allocator
        ComputeAllocatorFactory.register("flow", FlowComputeAllocator)
        
        allocator = ComputeAllocatorFactory.create("flow")
        assert isinstance(allocator, FlowComputeAllocator)


class TestMonarchFlowConfig:
    """Test the configuration class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = MonarchFlowConfig()
        assert config.provider == "fcp"
        assert config.default_instance_type is None
        assert config.startup_timeout == 300.0
        assert config.health_check_interval == 30.0
        assert config.custom_worker_script is None
        assert config.environment_vars == {}
        assert config.mount_paths == []
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = MonarchFlowConfig(
            provider="aws",
            default_instance_type="p4d.24xlarge",
            startup_timeout=600.0,
            environment_vars={"FOO": "bar"},
            mount_paths=["/data", "/models"]
        )
        assert config.provider == "aws"
        assert config.default_instance_type == "p4d.24xlarge"
        assert config.startup_timeout == 600.0
        assert config.environment_vars["FOO"] == "bar"
        assert "/data" in config.mount_paths
    
    def test_from_env(self, monkeypatch):
        """Test loading configuration from environment."""
        monkeypatch.setenv("MONARCH_FLOW_PROVIDER", "gcp")
        monkeypatch.setenv("MONARCH_FLOW_INSTANCE_TYPE", "a100-40gb")
        monkeypatch.setenv("MONARCH_FLOW_STARTUP_TIMEOUT", "450")
        monkeypatch.setenv("MONARCH_FLOW_HEALTH_CHECK_INTERVAL", "20")
        
        config = MonarchFlowConfig.from_env()
        assert config.provider == "gcp"
        assert config.default_instance_type == "h100"
        assert config.startup_timeout == 450.0
        assert config.health_check_interval == 20.0


class TestErrorHandling:
    """Test error handling classes."""
    
    def test_monarch_flow_error(self):
        """Test base error class."""
        error = MonarchFlowError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, MonarchFlowError)
    
    def test_allocation_error(self):
        """Test allocation error."""
        error = AllocationError("Failed to allocate GPU")
        assert isinstance(error, MonarchFlowError)
        assert "Failed to allocate GPU" in str(error)