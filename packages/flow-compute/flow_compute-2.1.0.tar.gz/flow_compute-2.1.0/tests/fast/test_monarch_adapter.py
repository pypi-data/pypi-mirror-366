"""
Unit tests for Monarch adapter components.

Tests the adapter that bridges Monarch and Flow's compute allocation.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock

from flow._internal.integrations.monarch import (
    ComputeRequirements,
    ProcessHandle,
    ComputeAllocator,
    FlowComputeAllocator,
)
from flow._internal.integrations.monarch_adapter import (
    AllocSpec,
    MonarchAllocation,
    MonarchLifecycleAdapter,
    MonarchAllocatorAdapter,
    MonarchFlowBackend,
    FlowProcMesh,
    create_monarch_backend,
)


class TestAllocSpec:
    """Test the AllocSpec data class."""
    
    def test_basic_spec(self):
        """Test creating basic allocation spec."""
        spec = AllocSpec(shape=(2, 4))
        assert spec.shape == (2, 4)
        assert spec.constraints == {}
    
    def test_spec_with_constraints(self):
        """Test spec with constraints."""
        spec = AllocSpec(
            shape=(1, 8),
            constraints={"gpu_type": "h100", "region": "us-east-1"}
        )
        assert spec.shape == (1, 8)
        assert spec.constraints["gpu_type"] == "h100"
        assert spec.constraints["region"] == "us-east-1"


class TestMonarchLifecycleAdapter:
    """Test the lifecycle adapter for Monarch."""
    
    @pytest.fixture
    def backend(self):
        """Create a mock backend."""
        return Mock()
    
    def test_initialization(self, backend):
        """Test adapter initialization."""
        adapter = MonarchLifecycleAdapter(host_idx=0, backend=backend)
        assert adapter.host_idx == 0
        assert adapter.backend is backend
        assert adapter.failed is False
        assert adapter.error_msg is None
        assert not adapter.ready.is_set()
    
    @pytest.mark.asyncio
    async def test_on_created(self, backend):
        """Test on_created callback."""
        adapter = MonarchLifecycleAdapter(0, backend)
        handle = ProcessHandle("test-id", "test-addr", {})
        
        await adapter.on_created(handle)
        # Should log but not change state
        assert not adapter.ready.is_set()
        assert not adapter.failed
    
    @pytest.mark.asyncio
    async def test_on_running(self, backend):
        """Test on_running callback."""
        adapter = MonarchLifecycleAdapter(0, backend)
        handle = ProcessHandle("test-id", "10.0.0.1:8000", {})
        
        await adapter.on_running(handle)
        
        # Should set ready
        assert adapter.ready.is_set()
        assert not adapter.failed
    
    @pytest.mark.asyncio
    async def test_on_failed(self, backend):
        """Test on_failed callback."""
        adapter = MonarchLifecycleAdapter(0, backend)
        handle = ProcessHandle("test-id", "test-addr", {})
        
        await adapter.on_failed(handle, "Test error")
        
        # Should mark as failed and set ready
        assert adapter.ready.is_set()
        assert adapter.failed
        assert adapter.error_msg == "Test error"
    
    @pytest.mark.asyncio
    async def test_on_stopped_before_ready(self, backend):
        """Test on_stopped when process stops before becoming ready."""
        adapter = MonarchLifecycleAdapter(0, backend)
        handle = ProcessHandle("test-id", "test-addr", {})
        
        await adapter.on_stopped(handle, "user_requested")
        
        # Should mark as failed if stopped before ready
        assert adapter.ready.is_set()
        assert adapter.failed
        assert "stopped before becoming ready" in adapter.error_msg


class TestMonarchAllocatorAdapter:
    """Test the Monarch allocator adapter."""
    
    @pytest.fixture
    def mock_allocator(self):
        """Create a mock compute allocator."""
        allocator = AsyncMock(spec=ComputeAllocator)
        return allocator
    
    @pytest.fixture
    def adapter(self, mock_allocator):
        """Create a MonarchAllocatorAdapter."""
        return MonarchAllocatorAdapter(mock_allocator)
    
    @pytest.mark.asyncio
    async def test_allocate_single_host(self, adapter, mock_allocator):
        """Test allocating a single host."""
        # Setup mock
        handle = ProcessHandle("task-123", "10.0.0.1:8000", {"gpu_count": 4})
        
        # Mock allocator to trigger lifecycle callbacks
        async def allocate_with_lifecycle(requirements, lifecycle):
            await lifecycle.on_created(handle)
            await lifecycle.on_running(handle)
            return handle
        
        mock_allocator.allocate.side_effect = allocate_with_lifecycle
        
        # Create spec
        spec = AllocSpec(shape=(1, 4), constraints={"gpu_type": "a100"})
        
        # Allocate
        allocation = await adapter.allocate(spec)
        
        # Verify allocation
        assert isinstance(allocation, MonarchAllocation)
        assert len(allocation.handles) == 1
        assert allocation.handles[0].id == "task-123"
        assert allocation.shape == (1, 4)
        assert allocation.addresses == ["10.0.0.1:8000"]
        
        # Verify allocator was called correctly
        mock_allocator.allocate.assert_called_once()
        call_args = mock_allocator.allocate.call_args
        requirements = call_args[0][0]
        assert requirements.gpu_count == 4
        assert requirements.gpu_type == "a100"
    
    @pytest.mark.asyncio
    async def test_allocate_multi_host(self, adapter, mock_allocator):
        """Test allocating multiple hosts."""
        # Setup mock to return different handles
        handles = [
            ProcessHandle(f"task-{i}", f"10.0.0.{i}:8000", {"gpu_count": 2})
            for i in range(3)
        ]
        
        # Mock allocator to trigger lifecycle callbacks
        async def allocate_with_lifecycle(requirements, lifecycle):
            idx = mock_allocator.allocate.call_count - 1
            handle = handles[idx]
            await lifecycle.on_created(handle)
            await lifecycle.on_running(handle)
            return handle
        
        mock_allocator.allocate.side_effect = allocate_with_lifecycle
        
        # Create spec for 3 hosts
        spec = AllocSpec(shape=(3, 2))
        
        # Allocate
        allocation = await adapter.allocate(spec)
        
        # Verify allocation
        assert len(allocation.handles) == 3
        assert allocation.shape == (3, 2)
        assert len(allocation.addresses) == 3
        assert allocation.addresses[0] == "10.0.0.0:8000"
        assert allocation.addresses[2] == "10.0.0.2:8000"
        
        # Verify allocator was called 3 times
        assert mock_allocator.allocate.call_count == 3
    
    @pytest.mark.asyncio
    async def test_allocate_with_failure(self, adapter, mock_allocator):
        """Test allocation when a host fails to start."""
        # First host succeeds, second fails
        handle1 = ProcessHandle("task-1", "10.0.0.1:8000", {})
        
        async def allocate_with_failure(requirements, lifecycle):
            if mock_allocator.allocate.call_count == 1:
                await lifecycle.on_created(handle1)
                await lifecycle.on_running(handle1)
                return handle1
            else:
                handle2 = ProcessHandle("task-2", "pending", {})
                await lifecycle.on_created(handle2)
                await lifecycle.on_failed(handle2, "Startup failed")
                return handle2
        
        mock_allocator.allocate.side_effect = allocate_with_failure
        mock_allocator.deallocate.return_value = None
        
        # Create spec for 2 hosts
        spec = AllocSpec(shape=(2, 1))
        
        # Allocate should fail
        with pytest.raises(RuntimeError, match="Host 1 failed to start"):
            await adapter.allocate(spec)
        
        # Verify cleanup was called
        mock_allocator.deallocate.assert_called()
    
    @pytest.mark.asyncio
    async def test_deallocate(self, adapter, mock_allocator):
        """Test deallocation."""
        # Create allocation
        handles = [ProcessHandle(f"task-{i}", f"addr-{i}", {}) for i in range(2)]
        allocation = MonarchAllocation(handles=handles, shape=(2, 1), addresses=["addr-0", "addr-1"])
        
        # Store handles
        for handle in handles:
            adapter._handles[handle.id] = handle
        
        # Deallocate
        await adapter.deallocate(allocation)
        
        # Verify all handles were deallocated
        assert mock_allocator.deallocate.call_count == 2
        assert len(adapter._handles) == 0
    
    @pytest.mark.asyncio
    async def test_health_check_all(self, adapter, mock_allocator):
        """Test checking health of all processes."""
        # Setup handles
        adapter._handles = {
            "task-1": ProcessHandle("task-1", "addr-1", {}),
            "task-2": ProcessHandle("task-2", "addr-2", {}),
        }
        
        # Mock health check results
        mock_allocator.health_check.side_effect = [True, False]
        
        # Check health
        results = await adapter.health_check_all()
        
        # Verify results
        assert results["task-1"] is True
        assert results["task-2"] is False
        assert mock_allocator.health_check.call_count == 2


class TestMonarchFlowBackend:
    """Test the Monarch Flow backend."""
    
    @pytest.fixture
    def mock_allocator(self):
        """Create a mock allocator."""
        return AsyncMock(spec=ComputeAllocator)
    
    @pytest.fixture
    def backend(self, mock_allocator):
        """Create a backend with mock allocator."""
        return MonarchFlowBackend(allocator=mock_allocator)
    
    @pytest.mark.asyncio
    async def test_create_proc_mesh(self, backend, mock_allocator):
        """Test creating a process mesh."""
        # Setup mock
        handles = [ProcessHandle("task-1", "10.0.0.1:8000", {})]
        
        # Configure allocate to trigger lifecycle events
        async def allocate_side_effect(requirements, lifecycle):
            # Trigger lifecycle events
            await lifecycle.on_created(handles[0])
            await lifecycle.on_running(handles[0])
            return handles[0]
        
        mock_allocator.allocate.side_effect = allocate_side_effect
        
        # Create mesh
        mesh = await backend.create_proc_mesh(shape=(1, 4), constraints={"gpu_type": "a100"})
        
        # Verify mesh
        assert isinstance(mesh, FlowProcMesh)
        assert mesh.shape == (1, 4)
        assert len(mesh.addresses) == 1
        assert mesh.addresses[0] == "10.0.0.1:8000"
    
    @pytest.mark.asyncio
    async def test_stop_all(self, backend, mock_allocator):
        """Test stopping all meshes."""
        # Create a mesh first
        handles = [ProcessHandle("task-1", "addr-1", {})]
        
        # Configure allocate to trigger lifecycle events
        async def allocate_side_effect(requirements, lifecycle):
            await lifecycle.on_created(handles[0])
            await lifecycle.on_running(handles[0])
            return handles[0]
        
        mock_allocator.allocate.side_effect = allocate_side_effect
        mesh = await backend.create_proc_mesh(shape=(1, 1))
        
        # Stop all
        await backend.stop_all()
        
        # Verify cleanup
        assert len(backend._proc_meshes) == 0


class TestFlowProcMesh:
    """Test the Flow process mesh."""
    
    @pytest.fixture
    def allocation(self):
        """Create a mock allocation."""
        handles = [
            ProcessHandle("task-1", "10.0.0.1:8000", {}),
            ProcessHandle("task-2", "10.0.0.2:8000", {}),
        ]
        return MonarchAllocation(
            handles=handles,
            shape=(2, 1),
            addresses=["10.0.0.1:8000", "10.0.0.2:8000"]
        )
    
    @pytest.fixture
    def backend(self):
        """Create a mock backend."""
        backend = Mock()
        backend._adapter = AsyncMock()
        return backend
    
    @pytest.fixture
    def mesh(self, allocation, backend):
        """Create a process mesh."""
        return FlowProcMesh(allocation, backend)
    
    def test_properties(self, mesh):
        """Test mesh properties."""
        assert mesh.shape == (2, 1)
        assert mesh.addresses == ["10.0.0.1:8000", "10.0.0.2:8000"]
    
    @pytest.mark.asyncio
    async def test_stop(self, mesh, backend):
        """Test stopping a mesh."""
        await mesh.stop()
        
        # Verify deallocate was called
        backend._adapter.deallocate.assert_called_once()
        assert mesh._stopped is True
        
        # Stopping again should do nothing
        backend._adapter.deallocate.reset_mock()
        await mesh.stop()
        backend._adapter.deallocate.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_health_check(self, mesh, backend, allocation):
        """Test health checking."""
        # Mock health check results
        backend._allocator = AsyncMock()
        backend._allocator.health_check.side_effect = [True, False]
        
        results = await mesh.health_check()
        
        assert results["task-1"] is True
        assert results["task-2"] is False
    
    def test_spawn_not_implemented(self, mesh):
        """Test that spawn raises NotImplementedError."""
        with pytest.raises(NotImplementedError):
            asyncio.run(mesh.spawn("test", Mock))


class TestCreateMonarchBackend:
    """Test the convenience function for creating backends."""
    
    @pytest.mark.asyncio
    async def test_create_backend(self):
        """Test creating a backend with defaults."""
        backend = await create_monarch_backend()
        assert isinstance(backend, MonarchFlowBackend)
        assert backend._config.provider == "fcp"
    
    @pytest.mark.asyncio
    async def test_create_backend_with_options(self):
        """Test creating a backend with custom options."""
        backend = await create_monarch_backend(
            provider="aws",
            default_instance_type="p4d.24xlarge",
            startup_timeout=900.0
        )
        assert backend._config.provider == "aws"
        assert backend._config.default_instance_type == "p4d.24xlarge"
        assert backend._config.startup_timeout == 900.0