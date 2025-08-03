"""Tests for decorator-based remote function execution using real behavior.

These tests verify the decorator pattern implementation without excessive mocking,
focusing on testing actual behavior rather than mock interactions.
"""

from unittest.mock import Mock, patch

import pytest

from flow import FlowApp
from flow._internal.config import Config
from flow.api.decorators import RemoteFunction, function
from flow.api.models import AvailableInstance, Task, TaskStatus
from tests.support.framework import TaskBuilder


class TestDecoratorBehavior:
    """Test the real behavior of decorator-based function execution."""

    @pytest.fixture
    def flow_app(self):
        """Create a real FlowApp instance with minimal config."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )

        # Create real FlowApp
        app = FlowApp(config=config)

        # Mock only the provider interaction
        mock_provider = Mock()
        mock_provider.prepare_task_config = lambda x: x  # Pass through

        # Mock task submission to return a realistic task
        def mock_submit(instance_type, config, **kwargs):
            task = TaskBuilder() \
                .with_id("task-123") \
                .with_name(config.name) \
                .with_status(TaskStatus.COMPLETED) \
                .with_instance_type(instance_type) \
                .build()
            # The decorator checks task.status as a string
            task.status = "completed"
            # Create a mock that has the id attribute for _extract_result
            task_mock = Mock(spec=Task)
            task_mock.status = "completed"
            task_mock.id = "task-123"
            task_mock.task_id = "task-123"
            # Mock the result() method to return expected data
            task_mock.result.return_value = {"status": "completed", "task_id": "task-123"}
            for attr in ['name', 'instance_type', 'num_instances', 'region', 'cost_per_hour', 'created_at']:
                setattr(task_mock, attr, getattr(task, attr))
            return task_mock

        mock_provider.submit_task = Mock(side_effect=mock_submit)
        mock_provider.find_instances.return_value = [
            AvailableInstance(
                allocation_id="alloc-123",
                instance_type="a100.80gb.sxm4.1x",
                region="us-east-1",
                price_per_hour=3.5
            )
        ]

        with patch.object(app, '_ensure_provider', return_value=mock_provider):
            yield app, mock_provider

    def test_function_decoration_creates_remote_function(self, flow_app):
        """Test that decorating a function creates a RemoteFunction instance."""
        app, _ = flow_app

        @app.function(gpu="a100.80gb.sxm4.1x", memory=32768)
        def my_function(x: int, y: int = 10) -> int:
            return x + y

        # Verify it's wrapped properly
        assert isinstance(my_function, RemoteFunction)
        assert my_function.func_name == "my_function"
        assert my_function.gpu == "a100.80gb.sxm4.1x"
        assert my_function.memory == 32768

        # Local execution should still work
        assert my_function(5) == 15
        assert my_function(5, y=20) == 25

    def test_wrapper_script_generation(self, flow_app):
        """Test the wrapper script generation for various argument types."""
        app, _ = flow_app

        @app.function()
        def process_data(
            input_path: str,
            output_path: str,
            batch_size: int = 32,
            use_gpu: bool = True,
            config: dict = None
        ) -> dict:
            return {"status": "processed"}

        # Test wrapper script with various arguments
        wrapper = process_data._create_wrapper_script(
            args=("data.csv", "output.csv"),
            kwargs={"batch_size": 64, "config": {"lr": 0.001}}
        )

        # Verify wrapper structure
        assert "import json" in wrapper
        assert "import sys" in wrapper
        assert "from pathlib import Path" in wrapper

        # Verify function import - the actual module path includes tests.unit
        assert "from tests.fast.test_decorator_real import process_data" in wrapper

        # Verify argument handling - the args are double-encoded in JSON
        assert 'data.csv' in wrapper
        assert 'output.csv' in wrapper
        assert 'batch_size' in wrapper
        assert '64' in wrapper
        assert 'lr' in wrapper
        assert '0.001' in wrapper

        # Verify result saving
        assert "result = process_data(*args, **kwargs)" in wrapper
        assert "/tmp/flow_result.json" in wrapper
        assert "json.dump" in wrapper

    def test_task_config_generation(self, flow_app):
        """Test TaskConfig generation from decorated function."""
        app, _ = flow_app

        @app.function(
            gpu="h100.80gb.sxm5.1x",
            cpu=8.0,
            memory=65536,  # 64GB
            image="pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime",
            env={"WANDB_API_KEY": "secret"},
            volumes={
                "/data": "training-data",
                "/models": {"name": "model-cache", "size_gb": 100}
            }
        )
        def train_model(config_path: str) -> dict:
            return {"trained": True}

        # Generate wrapper script first
        wrapper_script = train_model._create_wrapper_script(
            args=("config.yaml",),
            kwargs={}
        )

        # Generate TaskConfig with the wrapper as command
        config = train_model._build_task_config(wrapper_script)

        # Verify basic config
        assert config.name == "train_model-remote"
        assert config.instance_type == "h100.80gb.sxm5.1x"
        assert config.image == "pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime"

        # Verify command structure
        assert config.command[0] == "python"
        assert config.command[1] == "-c"
        assert len(config.command) == 3  # python, -c, script

        # Verify environment
        assert config.env["WANDB_API_KEY"] == "secret"

        # Verify volumes
        assert len(config.volumes) == 2
        volume_map = {v.mount_path: v for v in config.volumes}
        assert "/data" in volume_map
        assert volume_map["/data"].name == "training-data"
        assert "/models" in volume_map
        assert volume_map["/models"].size_gb == 100

    def test_remote_execution_flow(self, flow_app):
        """Test the complete remote execution flow."""
        app, mock_provider = flow_app

        @app.function(gpu="a100.80gb.sxm4.1x", memory=32768)
        def compute_result(a: int, b: int) -> int:
            return a * b

        # Execute remotely
        result = compute_result.remote(10, 20)

        # Result should be the placeholder from _extract_result
        assert result["status"] == "completed"
        assert result["task_id"] == "task-123"

        # Verify provider was called
        mock_provider.submit_task.assert_called_once()

        # Check the submitted config
        submit_call = mock_provider.submit_task.call_args
        submitted_config = submit_call.kwargs['config']

        assert submitted_config.name == "compute_result-remote"
        assert submitted_config.instance_type == "a100.80gb.sxm4.1x"
        # Memory is not set when GPU is specified
        assert submitted_config.min_gpu_memory_gb is None

        # Check the command contains the wrapper script
        assert len(submitted_config.command) == 3
        assert submitted_config.command[0] == "python"
        assert submitted_config.command[1] == "-c"
        wrapper_script = submitted_config.command[2]
        assert "compute_result" in wrapper_script
        assert "10" in wrapper_script and "20" in wrapper_script

    def test_spawn_async_execution(self, flow_app):
        """Test asynchronous execution with spawn()."""
        app, mock_provider = flow_app

        @app.function(gpu="h100.80gb.sxm5.1x")
        def long_running_task(duration: int) -> str:
            return f"Completed after {duration}s"

        # For spawn, we need to ensure the mock returns a task with an id attribute
        # when wait=False is used. Let's patch the run method directly
        with patch.object(app, 'run') as mock_run:
            # Create a mock task for async submission
            mock_task = Mock()
            mock_task.id = "task-123"
            mock_task.task_id = "task-123"
            mock_task.status = "running"
            mock_run.return_value = mock_task

            # Spawn task asynchronously
            task_id = long_running_task.spawn(3600)

            # Should return task ID immediately
            assert task_id == "task-123"

            # Verify run was called with wait=False
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert kwargs.get('wait') is False

    def test_json_serialization_error(self, flow_app):
        """Test helpful error for non-JSON serializable arguments."""
        app, _ = flow_app

        @app.function(gpu="a100.80gb.sxm4.1x")
        def process_object(obj):
            return str(obj)

        # Create non-serializable object
        class CustomClass:
            def __init__(self, value):
                self.value = value

        obj = CustomClass(42)

        # Should raise TypeError with helpful message
        with pytest.raises(TypeError) as exc_info:
            process_object.remote(obj)

        error = str(exc_info.value)
        assert "Cannot serialize" in error and "object to JSON" in error
        assert "CustomClass" in error
        assert "pickle.dump" in error

    def test_volume_specification_handling(self, flow_app):
        """Test various volume specification formats."""
        app, _ = flow_app

        @app.function(
            gpu="a100.80gb.sxm4.1x",
            volumes={
                "/simple": "existing-volume",
                "/sized": {"size_gb": 50},
                "/named": {"name": "my-cache", "size_gb": 100},
                "/by-id": {"volume_id": "vol-abc123"}
            }
        )
        def use_volumes() -> str:
            return "done"

        # Generate wrapper script first
        wrapper_script = use_volumes._create_wrapper_script(args=(), kwargs={})
        config = use_volumes._build_task_config(wrapper_script)

        # Check volume conversions
        assert len(config.volumes) == 4
        volume_map = {v.mount_path: v for v in config.volumes}

        # Simple string becomes name
        assert volume_map["/simple"].name == "existing-volume"

        # Size-only gets default values
        assert volume_map["/sized"].size_gb == 50

        # Named volume
        assert volume_map["/named"].name == "my-cache"
        assert volume_map["/named"].size_gb == 100

        # By ID
        assert volume_map["/by-id"].volume_id == "vol-abc123"

    def test_cpu_memory_handling(self, flow_app):
        """Test CPU and memory specification handling."""
        app, _ = flow_app

        # Test with GPU - memory becomes min_gpu_memory_gb
        @app.function(gpu="a100.80gb.sxm4.1x", memory=49152)  # 48GB
        def gpu_task() -> str:
            return "gpu"

        # Generate wrapper script first
        wrapper_script = gpu_task._create_wrapper_script(args=(), kwargs={})
        config = gpu_task._build_task_config(wrapper_script)
        assert config.instance_type == "a100.80gb.sxm4.1x"
        # When GPU is specified, memory is not used for min_gpu_memory_gb
        assert config.min_gpu_memory_gb is None

        # Test without GPU - memory is stored but not used in TaskConfig
        @app.function(memory=16384)  # 16GB
        def cpu_task() -> str:
            return "cpu"

        # Generate wrapper script first
        wrapper_script = cpu_task._create_wrapper_script(args=(), kwargs={})
        config = cpu_task._build_task_config(wrapper_script)
        assert config.min_gpu_memory_gb == 16
        assert config.instance_type is None

    def test_error_handling_in_wrapper(self, flow_app):
        """Test error handling in the wrapper script."""
        app, _ = flow_app

        @app.function()
        def may_fail(x: int) -> float:
            return 1.0 / x

        wrapper = may_fail._create_wrapper_script(args=(0,), kwargs={})

        # Verify error handling code
        assert "try:" in wrapper
        assert "except Exception as e:" in wrapper
        assert '"error": str(e)' in wrapper
        # Note: Current implementation doesn't use traceback module

    def test_realistic_ml_training_scenario(self, flow_app):
        """Test a realistic ML training scenario configuration."""
        app, _ = flow_app

        @app.function(
            gpu="a100.80gb.sxm4.8x",  # 8x A100 GPUs
            memory=524288,  # 512GB RAM
            image="nvcr.io/nvidia/pytorch:23.10-py3",
            volumes={
                "/datasets": "imagenet-dataset",
                "/checkpoints": {"name": "model-checkpoints", "size_gb": 500},
                "/cache": {"name": "docker-cache", "size_gb": 200}
            },
            env={
                "NCCL_DEBUG": "INFO",
                "CUDA_VISIBLE_DEVICES": "0,1,2,3,4,5,6,7"
            }
        )
        def train_large_model(
            config_path: str,
            resume_from: str = None,
            wandb_run_id: str = None
        ) -> dict:
            return {
                "final_loss": 0.0123,
                "best_checkpoint": "/checkpoints/best_model.pt"
            }

        # Test configuration generation
        # Generate wrapper script first
        wrapper_script = train_large_model._create_wrapper_script(
            args=("configs/training.yaml",),
            kwargs={"wandb_run_id": "run-12345"}
        )
        config = train_large_model._build_task_config(wrapper_script)

        assert config.name == "train_large_model-remote"
        assert config.instance_type == "a100.80gb.sxm4.8x"
        # When GPU is specified, memory is not used for min_gpu_memory_gb
        assert config.min_gpu_memory_gb is None
        assert config.image == "nvcr.io/nvidia/pytorch:23.10-py3"

        # Check volumes are properly configured
        assert len(config.volumes) == 3
        checkpoints_vol = next(v for v in config.volumes if v.mount_path == "/checkpoints")
        assert checkpoints_vol.size_gb == 500

        # Check environment variables
        assert config.env["NCCL_DEBUG"] == "INFO"
        assert config.env["CUDA_VISIBLE_DEVICES"] == "0,1,2,3,4,5,6,7"


class TestDecoratorPatternIntegration:
    """Test decorator pattern integration with Flow client."""

    @pytest.fixture
    def flow_app(self):
        """Create a real FlowApp instance with minimal config."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )

        # Create real FlowApp
        app = FlowApp(config=config)

        # Mock only the provider interaction
        mock_provider = Mock()
        mock_provider.prepare_task_config = lambda x: x  # Pass through

        # Mock task submission to return a realistic task
        def mock_submit(instance_type, config, **kwargs):
            task = TaskBuilder() \
                .with_id("task-123") \
                .with_name(config.name) \
                .with_status(TaskStatus.COMPLETED) \
                .with_instance_type(instance_type) \
                .build()
            # The decorator checks task.status as a string
            task.status = "completed"
            # Create a mock that has the id attribute for _extract_result
            task_mock = Mock(spec=Task)
            task_mock.status = "completed"
            task_mock.id = "task-123"
            task_mock.task_id = "task-123"
            # Mock the result() method to return expected data
            task_mock.result.return_value = {"status": "completed", "task_id": "task-123"}
            for attr in ['name', 'instance_type', 'num_instances', 'region', 'cost_per_hour', 'created_at']:
                setattr(task_mock, attr, getattr(task, attr))
            return task_mock

        mock_provider.submit_task = Mock(side_effect=mock_submit)
        mock_provider.find_instances.return_value = [
            AvailableInstance(
                allocation_id="alloc-123",
                instance_type="a100.80gb.sxm4.1x",
                region="us-east-1",
                price_per_hour=3.5
            )
        ]

        with patch.object(app, '_ensure_provider', return_value=mock_provider):
            yield app, mock_provider

    def test_global_app_instance(self, monkeypatch):
        """Test the global app instance works correctly."""
        # Set up test environment
        monkeypatch.setenv("FCP_API_KEY", "test-api-key")
        monkeypatch.setenv("FCP_DEFAULT_PROJECT", "test-project")

        # The global 'app' is lazy-loaded
        from flow import app as global_app

        # Should be able to use it as a decorator
        @global_app.function(gpu="a100.80gb.sxm4.1x")
        def global_decorated() -> str:
            return "success"

        assert isinstance(global_decorated, RemoteFunction)
        assert global_decorated.gpu == "a100.80gb.sxm4.1x"

        # After use, the underlying app should be a FlowApp
        actual_app = global_app() if callable(global_app) else global_app
        assert isinstance(actual_app, FlowApp)

    def test_standalone_function_decorator(self, monkeypatch):
        """Test the standalone @function decorator."""
        # Set up test environment
        monkeypatch.setenv("FCP_API_KEY", "test-api-key")
        monkeypatch.setenv("FCP_DEFAULT_PROJECT", "test-project")

        # Should use the global app instance
        @function(gpu="h100.80gb.sxm5.1x")
        def standalone_func(x: int) -> int:
            return x ** 2

        assert isinstance(standalone_func, RemoteFunction)
        assert standalone_func.gpu == "h100.80gb.sxm5.1x"

    def test_backward_compatibility(self, flow_app):
        """Test backward compatibility with 'environment' parameter."""
        app, _ = flow_app

        # Test 'environment' parameter (old name)
        @app.function(gpu="a100.80gb.sxm4.1x", environment={"OLD_PARAM": "value"})
        def old_style() -> str:
            return "legacy"

        wrapper = old_style._create_wrapper_script(args=(), kwargs={})
        config = old_style._build_task_config(wrapper)
        assert config.env["OLD_PARAM"] == "value"

        # Test both 'env' and 'environment' (env takes precedence)
        @app.function(
            gpu="a100.80gb.sxm4.1x",
            env={"NEW_PARAM": "new"},
            environment={"OLD_PARAM": "old"}
        )
        def both_styles() -> str:
            return "both"

        # env completely overrides environment (doesn't merge)
        assert both_styles.env["NEW_PARAM"] == "new"
        assert "OLD_PARAM" not in both_styles.env  # env takes full precedence
