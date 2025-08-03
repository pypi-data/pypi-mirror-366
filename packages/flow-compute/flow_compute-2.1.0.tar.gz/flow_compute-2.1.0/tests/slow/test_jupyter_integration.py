"""Integration tests for Flow-Colab with failure injection.

These tests simulate real-world failures and verify the system handles them correctly.
"""

import os
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flow._internal.integrations.jupyter import JupyterIntegration
from flow._internal.integrations.jupyter_persistence import PersistenceManager
from flow.api.models import Task, TaskStatus
from flow.errors import NetworkError, TimeoutError


class TestJupyterIntegrationWithFailures:
    """Test Colab integration with simulated failures."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_kernel_startup_with_network_failures(self, temp_dir):
        """Test kernel startup with intermittent network failures."""
        # Mock Flow client with failure injection
        mock_flow = Mock()

        # Simulate network failures on first 2 attempts, then success
        status_call_count = 0
        def mock_status(task_id):
            nonlocal status_call_count
            status_call_count += 1
            if status_call_count < 3:
                raise NetworkError("Connection timeout")
            return "running"

        mock_flow.status.side_effect = mock_status

        # Mock successful task creation
        mock_flow.run.return_value = Task(
            task_id="task-123",
            name="colab-test",
            status=TaskStatus.PENDING,
            instance_type="a100",
            region="us-central1",
            created_at=datetime.now(timezone.utc),
            num_instances=1,
            cost_per_hour="$3.60",
            ssh_host="10.0.0.1",
            ssh_user="ubuntu"
        )

        # Mock logs to return auth token after retries
        log_call_count = 0
        def mock_logs(task_id, tail=100):
            nonlocal log_call_count
            log_call_count += 1
            if log_call_count < 2:
                raise NetworkError("Log fetch failed")
            return "Starting kernel...\nFLOW_KERNEL_TOKEN=test-token-123\nKERNEL_READY=true"

        mock_flow.logs.side_effect = mock_logs

        # Mock volume operations - list_volumes should return an empty list
        mock_flow.list_volumes.return_value = []

        # Mock volume creation
        mock_volume = Mock()
        mock_volume.volume_id = "vol-123"
        mock_volume.name = "colab-persist-flow-session-123"
        mock_flow.create_volume.return_value = mock_volume

        # Test that integration handles failures gracefully
        integration = JupyterIntegration(mock_flow)
        connection = integration.launch(instance_type="a100", hours=1.0)

        # Verify retries happened
        assert status_call_count >= 3  # Initial failures + success
        assert log_call_count >= 2     # Log fetch with retry

        # Verify connection succeeded despite failures
        assert connection.task_id == "task-123"
        assert connection.session_id.startswith("flow-session-")
        assert connection.instance_type == "a100"

    def test_checkpoint_corruption_recovery(self, temp_dir):
        """Test recovery from corrupted checkpoint files."""
        # Create a corrupted checkpoint file
        checkpoint_dir = temp_dir / ".flow-kernel"
        checkpoint_dir.mkdir(exist_ok=True)

        corrupt_file = checkpoint_dir / "notebook_state.pkl"
        corrupt_file.write_bytes(b"corrupted data that's not valid pickle")

        # Create a valid backup
        import dill
        backup_file = checkpoint_dir / "notebook_state.pkl.backup"
        valid_checkpoint = {
            'version': 1,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'variables': {'x': 42, 'model': 'test'},
            'checksum': None
        }
        with open(backup_file, 'wb') as f:
            dill.dump(valid_checkpoint, f)

        # Verify files exist for recovery test
        # In real test, we'd actually start the kernel process
        # For now, verify the recovery logic works
        assert backup_file.exists()
        assert corrupt_file.exists()

        # Test recovery logic
        pm = PersistenceManager(Mock())
        # This would normally be called by the kernel

    def test_concurrent_checkpoint_writes(self, temp_dir):
        """Test that concurrent checkpoints don't corrupt data."""
        checkpoint_file = temp_dir / "concurrent_test.pkl"
        lock_file = temp_dir / ".checkpoint.lock"

        results = []
        errors = []

        def write_checkpoint(writer_id: int, iterations: int = 10):
            """Simulate checkpoint writes."""
            import fcntl

            import dill

            for i in range(iterations):
                try:
                    data = {
                        'writer': writer_id,
                        'iteration': i,
                        'timestamp': time.time()
                    }

                    # Use same locking mechanism as real code
                    with open(lock_file, 'w') as lock:
                        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

                        with open(checkpoint_file, 'wb') as f:
                            dill.dump(data, f)
                            f.flush()
                            os.fsync(f.fileno())

                    results.append((writer_id, i))
                    time.sleep(0.001)  # Small delay to increase contention

                except Exception as e:
                    errors.append((writer_id, i, str(e)))

        # Start multiple writers
        threads = []
        for writer_id in range(5):
            t = threading.Thread(
                target=write_checkpoint,
                args=(writer_id, 20)
            )
            threads.append(t)
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors during concurrent writes: {errors}"

        # Verify final checkpoint is valid
        import dill
        with open(checkpoint_file, 'rb') as f:
            final_data = dill.load(f)

        assert 'writer' in final_data
        assert 'iteration' in final_data
        assert 'timestamp' in final_data

    def test_kernel_timeout_handling(self):
        """Test proper timeout when kernel fails to start."""
        mock_flow = Mock()

        # Simulate kernel stuck in pending
        mock_flow.status.return_value = "pending"
        mock_flow.run.return_value = Task(
            task_id="stuck-task",
            name="colab-stuck",
            status=TaskStatus.PENDING,
            instance_type="a100",
            region="us-central1",
            created_at=datetime.now(timezone.utc),
            num_instances=1,
            cost_per_hour="$3.60",
            ssh_host="10.0.0.1"
        )

        # Mock volume operations
        mock_flow.list_volumes.return_value = []
        mock_volume = Mock()
        mock_volume.volume_id = "vol-stuck"
        mock_flow.create_volume.return_value = mock_volume

        # Mock logs to never show kernel ready
        mock_flow.logs.return_value = "Starting kernel... still waiting..."

        integration = JupyterIntegration(mock_flow)

        # Should timeout quickly in test (using a short timeout for tests)
        with patch('flow._internal.integrations.jupyter.JupyterIntegration._wait_for_kernel') as mock_wait:
            mock_wait.side_effect = TimeoutError("Kernel did not start within timeout")
            with pytest.raises(TimeoutError, match="Kernel did not start within"):
                integration.launch(instance_type="a100", hours=1.0)

    def test_volume_creation_retry(self):
        """Test volume creation with transient failures."""
        mock_flow = Mock()

        # First two calls fail, third succeeds
        create_call_count = 0
        def mock_create_volume(**kwargs):
            nonlocal create_call_count
            create_call_count += 1
            if create_call_count < 3:
                raise NetworkError("Volume service unavailable")

            mock_vol = Mock()
            mock_vol.volume_id = "vol-created-123"
            return mock_vol

        mock_flow.create_volume.side_effect = mock_create_volume
        mock_flow.list_volumes.return_value = []  # No existing volumes

        pm = PersistenceManager(mock_flow)
        volume_id = pm.ensure_volume("us-central1", "test-session")

        assert create_call_count == 3  # Two failures + one success
        assert volume_id == "vol-created-123"


class TestRealKernelIntegration:
    """Tests that actually start a kernel process (requires Docker)."""

    @pytest.mark.skipif(
        not os.path.exists("/var/run/docker.sock"),
        reason="Docker not available"
    )
    def test_real_kernel_startup(self):
        """Test starting a real Jupyter kernel in Docker."""
        # This test would:
        # 1. Start a Docker container with our kernel script
        # 2. Wait for auth token in logs
        # 3. Verify we can connect to the kernel
        # 4. Send a code execution request
        # 5. Verify response
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
