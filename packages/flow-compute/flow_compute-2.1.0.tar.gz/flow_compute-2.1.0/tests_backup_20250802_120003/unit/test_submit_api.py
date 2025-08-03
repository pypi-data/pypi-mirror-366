"""Test the new submit() API."""

import time
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from flow import Flow
from flow.api.models import AvailableInstance, Task, TaskStatus, Volume
from flow.core.resources.matcher import NoMatchingInstanceError
from flow.errors import ValidationError
from tests.conftest import create_mock_config


class TestSubmitAPI:
    """Test Flow.submit() method."""

    def setup_method(self):
        # Create a mock config to avoid interactive setup
        mock_config = create_mock_config(auth_token="test_key", project="test_project", api_url="https://api.test.com")

        self.flow = Flow(config=mock_config)
        # Mock the provider
        self.mock_provider = Mock()
        self.flow._provider = self.mock_provider

        # Mock prepare_task_config to return config unchanged
        self.mock_provider.prepare_task_config.side_effect = lambda x: x

        # Mock is_volume_id to identify volume IDs vs names
        self.mock_provider.is_volume_id.side_effect = lambda x: x.startswith("vol_")

        # Mock catalog for instance matching
        self.mock_provider.find_instances.return_value = [
            AvailableInstance(
                allocation_id="alloc_123",
                instance_type="a100.80gb.sxm4.1x",
                region="us-east-1",
                price_per_hour=5.0,
                gpu_count=1,
                status="available"
            )
        ]

        # Mock task submission
        self.mock_task = Task(
            task_id="task_123",
            name="flow-submit-test",
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            instance_type="a100.80gb.sxm4.1x",
            num_instances=1,
            region="us-east-1",
            cost_per_hour="$5.00",
            _provider=self.mock_provider
        )
        self.mock_provider.submit_task.return_value = self.mock_task

    def test_simple_gpu_job(self):
        """Test simple GPU job submission."""
        task = self.flow.submit("python train.py", gpu="a100")

        assert task.task_id == "task_123"
        assert task.name.startswith("flow-submit-")

        # Check that run() was called via submit_task
        self.mock_provider.submit_task.assert_called_once()
        call_args = self.mock_provider.submit_task.call_args

        # Check task config
        config = call_args.kwargs["config"]
        assert config.command == "python train.py"
        assert config.image == "ubuntu:22.04"
        assert config.instance_type == "a100.80gb.sxm4.1x"

    def test_gpu_with_count(self):
        """Test GPU with count specification."""
        # Update catalog to have 4x instance
        self.mock_provider.find_instances.return_value = [
            AvailableInstance(
                allocation_id="alloc_456",
                instance_type="a100.80gb.sxm4.4x",
                region="us-east-1",
                price_per_hour=20.0,
                gpu_count=4,
                status="available"
            )
        ]

        task = self.flow.submit("python train.py", gpu="a100:4")

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        assert config.instance_type == "a100.80gb.sxm4.4x"

    def test_explicit_instance_type(self):
        """Test explicit instance type usage."""
        # When explicit instance_type is provided, it still goes through
        # flow.run() which will validate and find available instances
        task = self.flow.submit("python train.py", instance_type="a100.80gb.sxm4.1x")

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        assert config.instance_type == "a100.80gb.sxm4.1x"

        # With explicit instance type, provider handles validation internally

    def test_volume_url_single(self):
        """Test single volume URL."""
        # Mock volume lookup
        self.mock_provider.list_volumes.return_value = [
            Volume(volume_id="vol_123", name="training-data", size_gb=100, region="us-east-1", interface="block", created_at=datetime.now())
        ]

        task = self.flow.submit(
            "python train.py",
            gpu="a100",
            mounts="volume://training-data"
        )

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        assert len(config.volumes) == 1
        assert config.volumes[0].volume_id == "vol_123"
        assert config.volumes[0].mount_path == "/mnt"

    def test_volume_url_multiple(self):
        """Test multiple volume URLs."""
        # Mock volume lookups
        self.mock_provider.list_volumes.return_value = [
            Volume(volume_id="vol_data", name="dataset", size_gb=100, region="us-east-1", interface="block", created_at=datetime.now()),
            Volume(volume_id="vol_models", name="models", size_gb=100, region="us-east-1", interface="block", created_at=datetime.now())
        ]

        task = self.flow.submit(
            "python train.py",
            mounts={
                "/datasets": "volume://dataset",
                "/checkpoints": "volume://models"
            }
        )

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        assert len(config.volumes) == 2

        # Check mount paths
        mount_paths = {v.mount_path: v.volume_id for v in config.volumes}
        assert mount_paths["/datasets"] == "vol_data"
        assert mount_paths["/checkpoints"] == "vol_models"

    def test_volume_id_direct(self):
        """Test direct volume ID usage."""
        task = self.flow.submit(
            "python train.py",
            mounts="volume://vol_existing123"
        )

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        assert config.volumes[0].volume_id == "vol_existing123"

        # Should not call list_volumes for direct IDs
        self.mock_provider.list_volumes.assert_not_called()

    def test_volume_auto_creation(self):
        """Test automatic volume creation."""
        # Mock empty volume list
        self.mock_provider.list_volumes.return_value = []

        # Mock volume creation
        mock_volume = Mock()
        mock_volume.volume_id = "vol_new123"
        self.mock_provider.create_volume.return_value = mock_volume

        task = self.flow.submit(
            "python train.py",
            mounts="volume://new-dataset"
        )

        # Should have created volume
        self.mock_provider.create_volume.assert_called_once_with(
            size_gb=100,
            name="new-dataset"
        )

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        assert config.volumes[0].volume_id == "vol_new123"

    def test_invalid_gpu_string(self):
        """Test error on invalid GPU string."""
        with pytest.raises(ValidationError) as exc:
            self.flow.submit("python train.py", gpu="invalid::gpu")

        assert "Invalid GPU string" in str(exc.value)
        assert "Use format: 'a100' or 'a100:4'" in str(exc.value)

    def test_unknown_gpu_type(self):
        """Test error on unknown GPU type."""
        with pytest.raises(ValidationError) as exc:
            self.flow.submit("python train.py", gpu="rtx4090")

        assert "Unknown GPU type: rtx4090" in str(exc.value)
        assert "Supported GPUs:" in str(exc.value)

    def test_no_matching_instances(self):
        """Test error when no instances match."""
        # Clear the catalog
        self.flow._catalog_cache = []

        with pytest.raises(NoMatchingInstanceError) as exc:
            self.flow.submit("python train.py", gpu="h100:8")

        assert "No instances found with 8x h100-80gb" in str(exc.value)

    def test_wait_parameter(self):
        """Test wait parameter is passed through to flow.run()."""
        # The wait parameter should be passed to flow.run()
        # We can't easily test the actual wait behavior in a unit test
        with patch.object(self.flow, 'run') as mock_run:
            mock_run.return_value = self.mock_task

            task = self.flow.submit("python train.py", gpu="a100", wait=True)

            # Check that run was called with wait=True
            mock_run.assert_called_once()
            _, kwargs = mock_run.call_args
            assert kwargs['wait'] is True

    def test_generated_task_name(self):
        """Test task name generation."""
        with patch('time.time', return_value=1234567890):
            task = self.flow.submit("python train.py")

            config = self.mock_provider.submit_task.call_args.kwargs["config"]
            assert config.name == "flow-submit-1234567890"

    def test_no_gpu_no_instance_type(self):
        """Test submission without GPU or instance type."""
        # Should work - flow.run() will find any available instance
        task = self.flow.submit("echo hello")

        config = self.mock_provider.submit_task.call_args.kwargs["config"]
        # When no instance type is specified, it defaults to "auto"
        assert config.instance_type == "auto"
        # The provider will handle auto-selection internally
        assert config.command == "echo hello"  # Command preserved as string
