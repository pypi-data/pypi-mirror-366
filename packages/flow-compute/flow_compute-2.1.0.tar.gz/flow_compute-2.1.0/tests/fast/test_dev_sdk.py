"""Tests for SDK dev environment functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from flow import Flow
from flow.api.dev import DevEnvironment
from flow.api.models import Task, TaskStatus
from flow.errors import DevVMNotFoundError, DevVMStartupError, DevContainerError


class TestDevEnvironment:
    """Test suite for DevEnvironment SDK interface."""
    
    @pytest.fixture
    def mock_flow(self):
        """Create mock Flow client."""
        flow = Mock(spec=Flow)
        flow._provider = Mock()
        return flow
    
    @pytest.fixture
    def dev_env(self, mock_flow):
        """Create DevEnvironment instance."""
        return DevEnvironment(mock_flow)
    
    def test_flow_dev_property(self):
        """Test that Flow.dev property returns DevEnvironment instance."""
        with patch('flow.api.client.Config.from_env') as mock_config:
            mock_config.return_value = Mock(api_key="test", project="test")
            flow = Flow()
            
            # First access should create instance
            dev1 = flow.dev
            assert isinstance(dev1, DevEnvironment)
            
            # Second access should return same instance
            dev2 = flow.dev
            assert dev1 is dev2
    
    def test_start_creates_new_vm(self, dev_env, mock_flow):
        """Test starting dev VM when none exists."""
        # Mock no existing VM
        dev_env._vm_manager.find_dev_vm = Mock(return_value=None)
        
        # Mock VM creation
        mock_vm = Mock(
            task_id="test-123",
            name="dev-abc123",
            ssh_host="1.2.3.4"
        )
        dev_env._vm_manager.create_dev_vm = Mock(return_value=mock_vm)
        
        # Mock wait functions
        with patch('flow.cli.commands.utils.wait_for_task', return_value="running"):
            vm = dev_env.start(instance_type="a100")
        
        assert vm == mock_vm
        dev_env._vm_manager.create_dev_vm.assert_called_once_with(
            instance_type="a100",
            ssh_keys=None,
            max_price_per_hour=None
        )
    
    def test_start_reuses_existing_vm(self, dev_env):
        """Test connecting to existing dev VM."""
        # Mock existing VM
        mock_vm = Mock(
            task_id="existing-123",
            name="dev-existing",
            ssh_host="1.2.3.4"
        )
        dev_env._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
        dev_env._vm_manager.create_dev_vm = Mock()
        
        vm = dev_env.start()
        
        assert vm == mock_vm
        # Should not create new VM
        dev_env._vm_manager.create_dev_vm.assert_not_called()
    
    def test_exec_without_vm_raises(self, dev_env):
        """Test exec without started VM raises error."""
        dev_env._vm_manager.find_dev_vm = Mock(return_value=None)
        
        with pytest.raises(DevVMNotFoundError):
            dev_env.exec("echo test")
    
    def test_exec_runs_command(self, dev_env, mock_flow):
        """Test executing command in container."""
        # Set up VM
        mock_vm = Mock(task_id="test-123")
        dev_env._current_vm = mock_vm
        
        # Mock executor
        mock_executor = Mock()
        mock_executor.execute_command = Mock(return_value=0)
        dev_env._executor = mock_executor
        
        # Run command
        exit_code = dev_env.exec("python train.py", image="python:3.11")
        
        assert exit_code == 0
        mock_executor.execute_command.assert_called_once_with(
            "python train.py",
            image="python:3.11",
            interactive=False
        )
    
    def test_reset_containers(self, dev_env):
        """Test resetting dev containers."""
        # Set up VM and executor
        mock_vm = Mock(task_id="test-123")
        dev_env._current_vm = mock_vm
        
        mock_executor = Mock()
        dev_env._executor = mock_executor
        
        # Reset containers
        dev_env.reset()
        
        mock_executor.reset_containers.assert_called_once()
    
    def test_stop_vm(self, dev_env):
        """Test stopping dev VM."""
        dev_env._vm_manager.stop_dev_vm = Mock(return_value=True)
        
        stopped = dev_env.stop()
        
        assert stopped is True
        assert dev_env._current_vm is None
        assert dev_env._executor is None
    
    def test_status_no_vm(self, dev_env):
        """Test status when no VM is running."""
        dev_env._vm_manager.find_dev_vm = Mock(return_value=None)
        
        status = dev_env.status()
        
        assert status["vm"] is None
        assert status["active_containers"] == 0
        assert status["containers"] == []
    
    def test_status_with_vm(self, dev_env):
        """Test status with running VM."""
        from datetime import datetime, timezone
        
        # Mock VM
        mock_vm = Mock(
            task_id="test-123",
            name="dev-abc",
            instance_type="h100",
            started_at=datetime.now(timezone.utc)
        )
        dev_env._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
        
        # Mock container status
        with patch.object(DevEnvironment, '_flow', create=True) as mock_flow_attr:
            mock_executor = Mock()
            mock_executor.get_container_status = Mock(return_value={
                "active_containers": 2,
                "containers": [
                    {"Names": "flow-dev-exec-abc", "Status": "Up 5 minutes"},
                    {"Names": "flow-dev-exec-def", "Status": "Up 10 minutes"}
                ]
            })
            
            with patch('flow.api.dev.DevContainerExecutor', return_value=mock_executor):
                status = dev_env.status()
        
        assert status["vm"]["name"] == "dev-abc"
        assert status["vm"]["instance_type"] == "h100"
        assert status["active_containers"] == 2
        assert len(status["containers"]) == 2
    
    def test_force_new_stops_existing(self, dev_env):
        """Test force_new parameter stops existing VM."""
        # Mock existing VM
        mock_existing = Mock(task_id="old-123")
        dev_env._vm_manager.find_dev_vm = Mock(side_effect=[mock_existing, None])
        dev_env._vm_manager.stop_dev_vm = Mock()
        
        # Mock new VM creation
        mock_new = Mock(task_id="new-123", ssh_host="1.2.3.4")
        dev_env._vm_manager.create_dev_vm = Mock(return_value=mock_new)
        
        with patch('flow.cli.commands.utils.wait_for_task', return_value="running"):
            vm = dev_env.start(force_new=True)
        
        # Should stop old VM
        dev_env._vm_manager.stop_dev_vm.assert_called_once()
        # Should create new VM
        assert vm == mock_new
    
    def test_connect_to_vm(self, dev_env, mock_flow):
        """Test connecting via SSH to dev VM."""
        # Mock existing VM
        mock_vm = Mock(task_id="test-123", name="dev-abc")
        dev_env._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
        
        # Connect to VM
        dev_env.connect()
        
        # Should call shell on flow client
        mock_flow.shell.assert_called_once_with(
            "test-123", 
            command=None
        )
    
    def test_ensure_started_existing_vm(self, dev_env):
        """Test ensure_started with existing VM."""
        # Mock existing VM
        mock_vm = Mock(task_id="existing-123", name="dev-existing")
        dev_env._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
        
        vm = dev_env.ensure_started()
        
        assert vm == mock_vm
        # Should not create new VM
        dev_env._vm_manager.create_dev_vm.assert_not_called()
    
    def test_ensure_started_creates_vm(self, dev_env):
        """Test ensure_started creates VM when none exists."""
        # Mock no existing VM
        dev_env._vm_manager.find_dev_vm = Mock(return_value=None)
        
        # Mock VM creation
        mock_vm = Mock(task_id="new-123", ssh_host="1.2.3.4")
        dev_env._vm_manager.create_dev_vm = Mock(return_value=mock_vm)
        
        with patch('flow.cli.commands.utils.wait_for_task', return_value="running"):
            vm = dev_env.ensure_started(instance_type="h100")
        
        assert vm == mock_vm
        dev_env._vm_manager.create_dev_vm.assert_called_once()
    
    def test_run_with_command(self, dev_env):
        """Test run method with command executes in container."""
        # Mock existing VM
        mock_vm = Mock(task_id="test-123")
        dev_env._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
        
        # Mock executor
        mock_executor = Mock()
        mock_executor.execute_command = Mock(return_value=0)
        
        with patch('flow.api.dev.DevContainerExecutor', return_value=mock_executor):
            exit_code = dev_env.run("python test.py", image="python:3.11")
        
        assert exit_code == 0
        mock_executor.execute_command.assert_called_once()
    
    def test_run_without_command(self, dev_env, mock_flow):
        """Test run method without command connects via SSH."""
        # Mock existing VM
        mock_vm = Mock(task_id="test-123")
        dev_env._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
        
        # Run without command
        result = dev_env.run()
        
        # Should connect via SSH
        mock_flow.shell.assert_called_once()
        # Should return VM object
        assert result == mock_vm
    
    def test_context_manager(self, mock_flow):
        """Test context manager functionality."""
        # Test with auto_stop=True
        with mock_flow.dev_context(auto_stop=True) as dev:
            # Mock VM
            mock_vm = Mock(task_id="test-123")
            dev._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
            dev._vm_manager.stop_dev_vm = Mock(return_value=True)
            
            # Use dev environment
            dev.ensure_started()
            
        # Should have called stop
        dev._vm_manager.stop_dev_vm.assert_called_once()
    
    def test_context_manager_no_auto_stop(self, mock_flow):
        """Test context manager without auto-stop."""
        with mock_flow.dev_context(auto_stop=False) as dev:
            # Mock VM
            mock_vm = Mock(task_id="test-123")
            dev._vm_manager.find_dev_vm = Mock(return_value=mock_vm)
            dev._vm_manager.stop_dev_vm = Mock()
            
            # Use dev environment
            dev.ensure_started()
            
        # Should NOT have called stop
        dev._vm_manager.stop_dev_vm.assert_not_called()
    
    def test_exec_with_retry(self, dev_env):
        """Test exec with retry on transient failures."""
        # Set up VM
        mock_vm = Mock(task_id="test-123")
        dev_env._current_vm = mock_vm
        
        # Mock executor to fail once then succeed
        mock_executor = Mock()
        mock_executor.execute_command = Mock(
            side_effect=[
                DevContainerError("Network timeout"),
                0  # Success on retry
            ]
        )
        dev_env._executor = mock_executor
        
        # Should succeed after retry
        exit_code = dev_env.exec("echo test", retries=2)
        assert exit_code == 0
        assert mock_executor.execute_command.call_count == 2
    
    def test_exec_no_retry_on_permanent_errors(self, dev_env):
        """Test exec doesn't retry permanent errors."""
        # Set up VM
        mock_vm = Mock(task_id="test-123")
        dev_env._current_vm = mock_vm
        
        # Mock executor to fail with permanent error
        mock_executor = Mock()
        mock_executor.execute_command = Mock(
            side_effect=DevContainerError("Docker: command not found")
        )
        dev_env._executor = mock_executor
        
        # Should fail immediately without retry
        with pytest.raises(DevContainerError, match="Docker: command not found"):
            dev_env.exec("echo test", retries=3)
        
        # Should only try once
        assert mock_executor.execute_command.call_count == 1
    
    def test_improved_error_messages(self, dev_env):
        """Test that errors have helpful suggestions."""
        dev_env._vm_manager.find_dev_vm = Mock(return_value=None)
        
        with pytest.raises(DevVMNotFoundError) as exc_info:
            dev_env.exec("test")
        
        error = exc_info.value
        assert "flow.dev.start()" in str(error)
        assert "flow.dev.ensure_started()" in str(error)