"""Unit tests for SSH waiter functionality."""

import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from flow.api.models import Task
from flow.providers.fcp.ssh_waiter import (
    ExponentialBackoffSSHWaiter,
    SSHConnectionInfo,
    SSHTimeoutError
)


class TestSSHWaiter:
    """Test SSH waiter functionality."""
    
    def test_ssh_connection_info_creation(self):
        """Test SSHConnectionInfo dataclass creation."""
        info = SSHConnectionInfo(
            host="192.168.1.100",
            port=22,
            user="ubuntu",
            key_path=Path("/home/user/.ssh/id_rsa"),
            task_id="task-123"
        )
        
        assert info.host == "192.168.1.100"
        assert info.port == 22
        assert info.user == "ubuntu"
        assert info.key_path == Path("/home/user/.ssh/id_rsa")
        assert info.task_id == "task-123"
        assert info.destination == "ubuntu@192.168.1.100"
    
    def test_wait_for_ssh_success(self):
        """Test successful SSH connection."""
        waiter = ExponentialBackoffSSHWaiter()
        
        # Mock task
        task = Mock(spec=Task)
        task.task_id = "test-123"
        task.ssh_host = "192.168.1.100"
        task.ssh_port = 22
        task.ssh_user = "ubuntu"
        
        # Mock successful SSH test
        with patch.object(waiter, '_test_ssh_connection', return_value=True):
            with patch.object(waiter, '_get_ssh_key_path', return_value=Path("/tmp/key")):
                result = waiter.wait_for_ssh(task, timeout=10)
                
        assert isinstance(result, SSHConnectionInfo)
        assert result.host == "192.168.1.100"
        assert result.port == 22
        assert result.user == "ubuntu"
        
    def test_wait_for_ssh_timeout(self):
        """Test SSH connection timeout."""
        waiter = ExponentialBackoffSSHWaiter()
        
        # Mock task
        task = Mock(spec=Task)
        task.task_id = "test-123"
        task.ssh_host = "192.168.1.100"
        task.ssh_port = 22
        task.ssh_user = "ubuntu"
        task.created_at = None
        
        # Mock failed SSH tests
        with patch.object(waiter, '_test_ssh_connection', return_value=False):
            with patch.object(waiter, '_get_ssh_key_path', return_value=Path("/tmp/key")):
                with pytest.raises(SSHTimeoutError) as exc_info:
                    waiter.wait_for_ssh(task, timeout=1, probe_interval=0.1)
                    
        assert "SSH connection timeout" in str(exc_info.value)
        
    def test_exponential_backoff(self):
        """Test exponential backoff timing."""
        waiter = ExponentialBackoffSSHWaiter()
        waiter.backoff_multiplier = 2.0
        waiter.max_backoff = 10
        
        # Track call times
        call_times = []
        
        def mock_test_ssh(conn):
            call_times.append(time.time())
            # Fail first 3 times, then succeed
            return len(call_times) >= 4
            
        # Mock task
        task = Mock(spec=Task)
        task.task_id = "test-123"
        task.ssh_host = "192.168.1.100"
        task.ssh_port = 22
        task.ssh_user = "ubuntu"
        
        with patch.object(waiter, '_test_ssh_connection', side_effect=mock_test_ssh):
            with patch.object(waiter, '_get_ssh_key_path', return_value=Path("/tmp/key")):
                start = time.time()
                waiter.wait_for_ssh(task, timeout=30, probe_interval=1.0)
                
        # Verify backoff pattern
        # Initial delay: 1.0s
        # Second delay: 2.0s
        # Third delay: 4.0s
        assert len(call_times) == 4
        
        # Check intervals (with some tolerance)
        intervals = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]
        assert 0.8 < intervals[0] < 1.2  # ~1s
        assert 1.8 < intervals[1] < 2.2  # ~2s
        assert 3.8 < intervals[2] < 4.2  # ~4s
        
    def test_ssh_test_connection_success(self):
        """Test SSH connection test with successful response."""
        waiter = ExponentialBackoffSSHWaiter()
        
        connection = SSHConnectionInfo(
            host="192.168.1.100",
            port=22,
            user="ubuntu",
            key_path=Path("/tmp/key"),
            task_id="test-123"
        )
        
        # Mock successful subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "SSH_TEST_OK"
        
        with patch('subprocess.run', return_value=mock_result) as mock_run:
            result = waiter._test_ssh_connection(connection)
            
        assert result is True
        
        # Verify SSH command construction
        call_args = mock_run.call_args[0][0]
        assert "ssh" in call_args
        assert "-p" in call_args
        assert "22" in call_args
        assert "StrictHostKeyChecking=no" in ' '.join(call_args)
        
    def test_ssh_test_connection_refused(self):
        """Test SSH connection test with connection refused."""
        waiter = ExponentialBackoffSSHWaiter()
        
        connection = SSHConnectionInfo(
            host="192.168.1.100",
            port=22,
            user="ubuntu",
            key_path=Path("/tmp/key"),
            task_id="test-123"
        )
        
        # Mock connection refused
        mock_result = Mock()
        mock_result.returncode = 255
        mock_result.stderr = "Connection refused"
        
        with patch('subprocess.run', return_value=mock_result):
            result = waiter._test_ssh_connection(connection)
            
        assert result is False
        
    def test_progress_callback(self):
        """Test progress callback is called during wait."""
        waiter = ExponentialBackoffSSHWaiter()
        
        # Mock task
        task = Mock(spec=Task)
        task.task_id = "test-123"
        task.ssh_host = "192.168.1.100"
        task.ssh_port = 22
        task.ssh_user = "ubuntu"
        
        # Track progress updates
        progress_updates = []
        
        def progress_callback(status):
            progress_updates.append(status)
            
        # Mock SSH test to fail a few times
        attempt_count = 0
        def mock_test_ssh(conn):
            nonlocal attempt_count
            attempt_count += 1
            return attempt_count >= 3
            
        with patch.object(waiter, '_test_ssh_connection', side_effect=mock_test_ssh):
            with patch.object(waiter, '_get_ssh_key_path', return_value=Path("/tmp/key")):
                waiter.wait_for_ssh(task, timeout=30, probe_interval=0.1, 
                                  progress_callback=progress_callback)
                
        # Should have received progress updates
        assert len(progress_updates) >= 2
        assert any("Waiting for SSH" in update for update in progress_updates)
        assert any("elapsed" in update for update in progress_updates)