"""Phase 3: Production startup script tests for LocalProvider."""

import time
from unittest.mock import MagicMock, patch

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus, VolumeSpec
from flow.providers.local.config import LocalTestConfig
from flow.providers.local.provider import LocalProvider


class TestLocalProviderPhase3:
    """Test production startup script integration."""

    def test_startup_script_generation(self):
        """Uses production startup scripts when available."""
        provider = LocalProvider(Config(provider="local"))

        # Check if FCP startup builder is available
        from flow.providers.local import executor
        if not executor.HAS_FCP_STARTUP_BUILDER:
            pytest.skip("FCP startup builder not available")

        # Ensure we're using FCP startup scripts
        assert provider.local_config.use_fcp_startup_scripts

        task = provider.submit_task("local", TaskConfig(
            name="test-startup",
            instance_type="cpu.small",
            command="echo 'User script'",
            env={"TEST": "123"}
        ))

        # Wait for completion
        for _ in range(20):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        logs = provider.get_task_logs(task.task_id)

        # Should see startup script markers if FCP builder worked
        # The exact markers depend on the FCP implementation
        assert "User script" in logs  # Our script should run

        # If production scripts are used, we might see additional setup
        print(f"Logs with production script:\n{logs}")

    def test_startup_script_fallback(self):
        """Falls back gracefully without startup script builder."""
        # Create a config with FCP scripts disabled
        config = LocalTestConfig(use_fcp_startup_scripts=False)

        with patch.object(LocalTestConfig, 'default', return_value=config):
            provider = LocalProvider(Config(provider="local"))
            assert not provider.local_config.use_fcp_startup_scripts

        task = provider.submit_task("local", TaskConfig(
            name="test-fallback",
            instance_type="cpu.small",
            command="echo 'Direct execution'"
        ))

        # Wait for completion
        time.sleep(0.5)
        logs = provider.get_task_logs(task.task_id)

        # Should see simple script output
        assert "Direct execution" in logs
        assert "Starting task test-fallback" in logs  # Simple script marker

    def test_startup_script_with_volumes(self):
        """Test startup script handles volumes correctly."""
        provider = LocalProvider(Config(provider="local"))

        # Create a volume
        volume = provider.create_volume(VolumeSpec(name="test-vol", size_gb=1))

        task = provider.submit_task("local", TaskConfig(
            name="test-volumes",
            instance_type="cpu.small",
            command="echo 'Testing with volumes'",
            volumes=[VolumeSpec(name="test-vol", size_gb=1, mount_path="/data")]
        ), volume_ids=[volume.volume_id])

        # Wait for completion
        for _ in range(20):
            time.sleep(0.1)
            task = provider.get_task(task.task_id)
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break

        assert task.status == TaskStatus.COMPLETED
        logs = provider.get_task_logs(task.task_id)
        assert "Testing with volumes" in logs

        # Clean up
        provider.delete_volume(volume.volume_id)

    def test_startup_script_error_handling(self):
        """Test handling of startup script generation errors."""
        # Mock FCP builder to raise an error
        with patch('flow.providers.local.executor.FCPStartupScriptBuilder') as mock_builder:
            mock_builder.side_effect = Exception("Mock error")

            provider = LocalProvider(Config(provider="local"))

            # Should fall back gracefully
            task = provider.submit_task("local", TaskConfig(
                name="test-error",
                instance_type="cpu.small",
                command="echo 'Should still work'"
            ))

            # Wait for completion
            for _ in range(10):
                time.sleep(0.2)
                task = provider.get_task(task.task_id)
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    break

            logs = provider.get_task_logs(task.task_id)

            # Should fall back to simple script
            assert "Should still work" in logs
            assert task.status == TaskStatus.COMPLETED

    def test_startup_script_validation_failure(self):
        """Test handling of invalid startup scripts."""
        # Mock FCP builder to return invalid script
        with patch('flow.providers.local.executor.FCPStartupScriptBuilder') as mock_builder_class:
            mock_builder = MagicMock()
            mock_script = MagicMock()
            mock_script.is_valid = False
            mock_script.validation_errors = ["Mock validation error"]
            mock_builder.build.return_value = mock_script
            mock_builder_class.return_value = mock_builder

            provider = LocalProvider(Config(provider="local"))

            # Should fall back when validation fails
            task = provider.submit_task("local", TaskConfig(
                name="test-invalid",
                instance_type="cpu.small",
                command="echo 'Fallback script'"
            ))

            # Wait for completion
            for _ in range(10):
                time.sleep(0.2)
                task = provider.get_task(task.task_id)
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    break

            logs = provider.get_task_logs(task.task_id)

            # Should use fallback script
            assert "Fallback script" in logs
            assert task.status == TaskStatus.COMPLETED


if __name__ == "__main__":
    # Run tests directly
    test = TestLocalProviderPhase3()

    print("Running Phase 3 tests...")

    print("1. Testing startup script generation...")
    try:
        test.test_startup_script_generation()
        print("✓ Startup script generation works")
    except Exception as e:
        if "FCP startup builder not available" in str(e):
            print("⚠ FCP startup builder not available - skipping")
        else:
            raise

    print("2. Testing startup script fallback...")
    test.test_startup_script_fallback()
    print("✓ Startup script fallback works")

    print("3. Testing startup script with volumes...")
    test.test_startup_script_with_volumes()
    print("✓ Startup scripts work with volumes")

    print("4. Testing error handling...")
    test.test_startup_script_error_handling()
    print("✓ Error handling works")

    print("5. Testing validation failure handling...")
    test.test_startup_script_validation_failure()
    print("✓ Validation failure handling works")

    print("\nAll Phase 3 tests passed! ✅")
