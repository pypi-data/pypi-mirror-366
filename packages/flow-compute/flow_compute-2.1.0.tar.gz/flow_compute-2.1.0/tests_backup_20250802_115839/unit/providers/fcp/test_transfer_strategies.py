"""Unit tests for file transfer strategies."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from flow.providers.fcp.ssh_waiter import SSHConnectionInfo
from flow.providers.fcp.transfer_strategies import (
    RsyncTransferStrategy,
    TransferError,
    TransferProgress,
    TransferResult
)


class TestTransferStrategies:
    """Test file transfer strategy implementations."""
    
    def test_transfer_progress_creation(self):
        """Test TransferProgress dataclass."""
        progress = TransferProgress(
            bytes_transferred=1024 * 1024,
            total_bytes=10 * 1024 * 1024,
            percentage=10.0,
            speed="2.5MB/s",
            eta="0:00:04",
            current_file="src/main.py"
        )
        
        assert progress.bytes_transferred == 1024 * 1024
        assert progress.total_bytes == 10 * 1024 * 1024
        assert progress.percentage == 10.0
        assert progress.speed == "2.5MB/s"
        assert progress.eta == "0:00:04"
        assert progress.current_file == "src/main.py"
        assert not progress.is_complete
        
        # Test completion
        complete_progress = TransferProgress(
            bytes_transferred=100,
            total_bytes=100,
            percentage=100.0,
            speed=None,
            eta=None,
            current_file=None
        )
        assert complete_progress.is_complete
        
    def test_transfer_result_creation(self):
        """Test TransferResult dataclass."""
        result = TransferResult(
            success=True,
            bytes_transferred=50 * 1024 * 1024,
            duration_seconds=10.0,
            files_transferred=150
        )
        
        assert result.success
        assert result.bytes_transferred == 50 * 1024 * 1024
        assert result.duration_seconds == 10.0
        assert result.files_transferred == 150
        assert result.transfer_rate == "5.00 MB/s"
        
    def test_rsync_find_executable(self):
        """Test rsync executable discovery."""
        strategy = RsyncTransferStrategy()
        
        # Should find rsync if installed
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout="/usr/bin/rsync\n")
            
            # Force re-discovery
            strategy.rsync_path = strategy._find_rsync()
            
            assert strategy.rsync_path == "/usr/bin/rsync"
            
    def test_rsync_command_construction(self):
        """Test rsync command building."""
        strategy = RsyncTransferStrategy()
        strategy.rsync_path = "/usr/bin/rsync"
        
        source = Path("/home/user/project")
        target = "/workspace"
        connection = SSHConnectionInfo(
            host="192.168.1.100",
            port=2222,
            user="ubuntu",
            key_path=Path("/home/user/.ssh/key"),
            task_id="test-123"
        )
        
        cmd = strategy._build_rsync_command(source, target, connection, None)
        
        # Verify command structure
        assert cmd[0] == "/usr/bin/rsync"
        assert "-avz" in cmd
        assert "--progress" in cmd
        assert "--human-readable" in cmd
        assert "--stats" in cmd
        
        # Verify SSH command
        ssh_idx = cmd.index("-e")
        ssh_cmd = cmd[ssh_idx + 1]
        assert "ssh -p 2222" in ssh_cmd
        assert f"-i {connection.key_path}" in ssh_cmd
        assert "StrictHostKeyChecking=no" in ssh_cmd
        
        # Verify source and destination
        assert f"{source}/" in cmd
        assert f"ubuntu@192.168.1.100:{target}/" in cmd
        
    def test_rsync_progress_parsing(self):
        """Test parsing of rsync progress output."""
        strategy = RsyncTransferStrategy()
        
        # Test file transfer progress
        line = "  32,768,000  78%    2.34MB/s    0:00:03"
        progress = strategy._parse_rsync_progress(line)
        
        assert progress is not None
        assert progress.bytes_transferred == 32_768_000
        assert progress.percentage == 78.0
        assert progress.speed == "2.34MB/s"
        assert progress.eta == "0:00:03"
        
        # Test filename line
        line = "src/main.py"
        progress = strategy._parse_rsync_progress(line)
        
        assert progress is not None
        assert progress.current_file == "src/main.py"
        
        # Test completion
        line = "xfr#1, to-chk=0/1"
        progress = strategy._parse_rsync_progress(line)
        
        assert progress is not None
        assert progress.percentage == 100.0
        assert progress.eta == "0:00:00"
        
    def test_transfer_with_exclude_patterns(self):
        """Test transfer with .flowignore patterns."""
        strategy = RsyncTransferStrategy()
        strategy.rsync_path = "/usr/bin/rsync"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir)
            
            # Create .flowignore
            flowignore = source / ".flowignore"
            flowignore.write_text("*.pyc\n__pycache__/\n.git/\n")
            
            # Test exclude file creation
            exclude_file = strategy._create_exclude_file(source)
            
            assert exclude_file is not None
            assert exclude_file.exists()
            
            # Read exclude patterns
            patterns = exclude_file.read_text().strip().split('\n')
            assert "*.pyc" in patterns
            assert "__pycache__/" in patterns
            assert ".git/" in patterns
            
            # Clean up
            exclude_file.unlink()
            
    def test_transfer_success(self):
        """Test successful file transfer."""
        strategy = RsyncTransferStrategy()
        strategy.rsync_path = "/usr/bin/rsync"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir)
            (source / "test.py").write_text("print('hello')")
            
            connection = SSHConnectionInfo(
                host="192.168.1.100",
                port=22,
                user="ubuntu",
                key_path=Path("/tmp/key"),
                task_id="test-123"
            )
            
            # Mock subprocess
            mock_process = Mock()
            mock_process.stdout = iter([
                "sending incremental file list",
                "test.py",
                "         100 100%    0.10kB/s    0:00:00",
                "Number of files transferred: 1",
                "Total transferred file size: 100",
            ])
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_process.stderr = Mock(read=lambda: "")
            
            with patch('subprocess.Popen', return_value=mock_process):
                result = strategy.transfer(source, "/workspace", connection)
                
            assert result.success
            assert result.files_transferred == 1
            assert result.bytes_transferred > 0
            
    def test_transfer_failure(self):
        """Test transfer failure handling."""
        strategy = RsyncTransferStrategy()
        strategy.rsync_path = "/usr/bin/rsync"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir)
            
            connection = SSHConnectionInfo(
                host="192.168.1.100",
                port=22,
                user="ubuntu",
                key_path=Path("/tmp/key"),
                task_id="test-123"
            )
            
            # Mock subprocess failure
            mock_process = Mock()
            mock_process.stdout = iter([])
            mock_process.returncode = 1
            mock_process.wait.return_value = None
            mock_process.stderr = Mock(read=lambda: "Connection refused")
            
            with patch('subprocess.Popen', return_value=mock_process):
                with pytest.raises(TransferError) as exc_info:
                    strategy.transfer(source, "/workspace", connection)
                    
            assert "rsync failed" in str(exc_info.value)
            
    def test_transfer_with_progress_callback(self):
        """Test transfer with progress callback."""
        strategy = RsyncTransferStrategy()
        strategy.rsync_path = "/usr/bin/rsync"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir)
            (source / "test.py").write_text("print('hello')")
            
            connection = SSHConnectionInfo(
                host="192.168.1.100",
                port=22,
                user="ubuntu",
                key_path=Path("/tmp/key"),
                task_id="test-123"
            )
            
            # Track progress updates
            progress_updates = []
            
            def progress_callback(progress):
                progress_updates.append(progress)
                
            # Mock subprocess with progress
            mock_process = Mock()
            mock_process.stdout = iter([
                "test.py",
                "         50  50%    1.00MB/s    0:00:01",
                "        100 100%    2.00MB/s    0:00:00",
                "Number of files transferred: 1",
            ])
            mock_process.returncode = 0
            mock_process.wait.return_value = None
            mock_process.stderr = Mock(read=lambda: "")
            
            with patch('subprocess.Popen', return_value=mock_process):
                result = strategy.transfer(
                    source, "/workspace", connection,
                    progress_callback=progress_callback
                )
                
            # Should have received progress updates
            assert len(progress_updates) >= 2
            
            # Check progress values
            file_update = next((p for p in progress_updates if p.current_file), None)
            assert file_update is not None
            assert file_update.current_file == "test.py"
            
            progress_update = next((p for p in progress_updates if p.percentage), None)
            assert progress_update is not None
            assert progress_update.percentage > 0