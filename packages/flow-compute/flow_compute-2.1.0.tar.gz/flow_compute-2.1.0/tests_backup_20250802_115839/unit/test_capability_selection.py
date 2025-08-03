"""Tests for capability-based GPU selection using real behavior.

These tests verify that GPU selection by capability (memory, compute) works
correctly, following the principle of making the right thing easy.

Instead of mocking everything, we test the actual logic of capability selection.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError as PydanticValidationError

from flow import Flow
from flow._internal.config import Config
from flow.api.models import AvailableInstance, Task, TaskConfig, TaskStatus
from flow.errors import ResourceNotAvailableError
from tests.support.framework import TaskConfigBuilder


def get_test_catalog():
    """Get test catalog data for capability selection tests."""
    return [
        {
            "name": "gpu.nvidia.h100",
            "instance_type": "gpu.nvidia.h100",
            "gpu_type": "h100",
            "gpu_count": 1,
            "price_per_hour": 5.0,
            "available": True,
            "gpu": {
                "model": "h100",
                "memory_gb": 80
            }
        },
        {
            "name": "gpu.nvidia.a100",
            "instance_type": "gpu.nvidia.a100",
            "gpu_type": "a100",
            "gpu_count": 1,
            "price_per_hour": 3.5,
            "available": True,
            "gpu": {
                "model": "a100",
                "memory_gb": 80
            }
        },
        {
            "name": "gpu.nvidia.a100-40gb",
            "instance_type": "gpu.nvidia.a100-40gb",
            "gpu_type": "a100",
            "gpu_count": 1,
            "price_per_hour": 2.0,
            "available": True,
            "gpu": {
                "model": "a100",
                "memory_gb": 40
            }
        },
        {
            "name": "gpu.nvidia.v100",
            "instance_type": "gpu.nvidia.v100",
            "gpu_type": "v100",
            "gpu_count": 1,
            "price_per_hour": 1.5,
            "available": True,
            "gpu": {
                "model": "v100",
                "memory_gb": 32
            }
        }
    ]


class TestCapabilityBasedSelection:
    """Test GPU selection by capability rather than explicit instance type."""

    @pytest.fixture
    def flow_with_catalog(self):
        """Create Flow instance with test catalog data."""
        # Create a real Config object with minimal requirements
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )

        # Create Flow instance
        flow = Flow(config=config)

        # Mock the provider's find_instances to return test catalog
        mock_provider = Mock()
        mock_provider.prepare_task_config = lambda x: x  # Pass through

        # Define test catalog with realistic GPU options
        test_instances = [
            AvailableInstance(
                allocation_id="alloc-h100",
                instance_type="gpu.nvidia.h100",
                region="us-east-1",
                price_per_hour=5.0,
                gpu_type="h100",
                gpu_count=1,
                memory_gb=80
            ),
            AvailableInstance(
                allocation_id="alloc-a100-80",
                instance_type="gpu.nvidia.a100",
                region="us-east-1",
                price_per_hour=3.5,
                gpu_type="a100",
                gpu_count=1,
                memory_gb=80
            ),
            AvailableInstance(
                allocation_id="alloc-a100-40",
                instance_type="gpu.nvidia.a100-40gb",
                region="us-east-1",
                price_per_hour=2.0,
                gpu_type="a100",
                gpu_count=1,
                memory_gb=40
            ),
            AvailableInstance(
                allocation_id="alloc-v100",
                instance_type="gpu.nvidia.v100",
                region="us-east-1",
                price_per_hour=1.5,
                gpu_type="v100",
                gpu_count=1,
                memory_gb=32
            )
        ]

        # Set up the mock provider to return our test instances
        mock_provider.find_instances.return_value = test_instances

        # Mock find_instances to return the right instance when queried by type
        def mock_find_instances(requirements, limit=10):
            if 'instance_type' in requirements:
                # Return the specific instance requested
                return [i for i in test_instances if i.instance_type == requirements['instance_type']][:limit]
            # Otherwise return all instances
            return test_instances[:limit]

        mock_provider.find_instances.side_effect = mock_find_instances

        # Mock the task submission with new interface
        mock_provider.submit_task.side_effect = lambda instance_type, config, **kwargs: Task(
            task_id=f"task-{instance_type}",
            name=config.name,
            status=TaskStatus.PENDING,
            instance_type=instance_type,  # Use the passed instance type
            num_instances=1,
            region="us-east-1",
            cost_per_hour="$1.00",
            created_at=datetime.now()
        )

        # Patch the provider creation
        with patch.object(flow, '_ensure_provider', return_value=mock_provider):
            yield flow, mock_provider, test_instances

    def test_min_gpu_memory_selects_cheapest(self, flow_with_catalog):
        """Test that min_gpu_memory_gb selects the cheapest suitable GPU."""
        flow, mock_provider, instances = flow_with_catalog

        # Mock the catalog loading to return properly formatted data
        test_catalog = get_test_catalog()

        # Patch the catalog loading
        with patch.object(flow, '_load_instance_catalog', return_value=test_catalog):
            # Request 80GB minimum
            config = TaskConfigBuilder() \
                .with_name("test-80gb") \
                .with_command("python train.py") \
                .build()

            # Remove instance_type and add min_gpu_memory_gb
            config_dict = config.model_dump()
            config_dict.pop('instance_type')
            config_dict['min_gpu_memory_gb'] = 80
            config = TaskConfig(**config_dict)

            # Run the task
            task = flow.run(config)

            # Verify the cheaper A100 80GB was selected over H100
            submit_call = mock_provider.submit_task.call_args
            # Instance type should be passed as keyword argument
            assert submit_call.kwargs['instance_type'] == "gpu.nvidia.a100"
            assert task.instance_type == "gpu.nvidia.a100"

    def test_min_gpu_memory_with_price_constraint(self, flow_with_catalog):
        """Test GPU selection with both memory and price constraints."""
        flow, mock_provider, instances = flow_with_catalog

        with patch.object(flow, '_load_instance_catalog', return_value=get_test_catalog()):
            # Request 40GB minimum with max price of $2.50/hr
            config_dict = {
                "name": "budget-task",
                "command": ["python", "inference.py"],
                "min_gpu_memory_gb": 40,
                "max_price_per_hour": 2.50
            }
            config = TaskConfig(**config_dict)

            # Run the task
            task = flow.run(config)

            # Should select A100 40GB ($2.00) not A100 80GB ($3.50)
            submit_call = mock_provider.submit_task.call_args
            assert submit_call.kwargs['instance_type'] == "gpu.nvidia.a100-40gb"
            assert task.instance_type == "gpu.nvidia.a100-40gb"

    def test_no_suitable_gpu_raises_error(self, flow_with_catalog):
        """Test that requesting unavailable GPU memory raises appropriate error."""
        flow, mock_provider, instances = flow_with_catalog

        with patch.object(flow, '_load_instance_catalog', return_value=get_test_catalog()):
            # Request 100GB minimum (not available)
            config_dict = {
                "name": "impossible-task",
                "command": ["python", "train.py"],
                "min_gpu_memory_gb": 100
            }
            config = TaskConfig(**config_dict)

            # Should raise error about no suitable GPUs
            with pytest.raises(ResourceNotAvailableError, match="No GPU instances found with at least 100GB"):
                flow.run(config)

    def test_price_constraint_eliminates_all_options(self, flow_with_catalog):
        """Test error when price constraint is too low."""
        flow, mock_provider, instances = flow_with_catalog

        with patch.object(flow, '_load_instance_catalog', return_value=get_test_catalog()):
            # Request 80GB with max price of $1.00/hr (impossible)
            config_dict = {
                "name": "too-cheap",
                "command": ["python", "train.py"],
                "min_gpu_memory_gb": 80,
                "max_price_per_hour": 1.00
            }
            config = TaskConfig(**config_dict)

            # Should raise error about price constraint
            with pytest.raises(ResourceNotAvailableError, match="under \\$1.0/hour"):
                flow.run(config)

    def test_capability_selection_logs_choice(self, flow_with_catalog, caplog):
        """Test that capability selection logs the chosen instance."""
        flow, mock_provider, instances = flow_with_catalog

        with patch.object(flow, '_load_instance_catalog', return_value=get_test_catalog()):
            config_dict = {
                "name": "logged-task",
                "command": ["echo", "test"],
                "min_gpu_memory_gb": 32
            }
            config = TaskConfig(**config_dict)

            # Run with logging captured
            import logging
            with caplog.at_level(logging.INFO):
                task = flow.run(config)

            # Should log the auto-selection
            assert "Auto-selected gpu.nvidia.v100" in caplog.text
            assert "$1.5/hour" in caplog.text

    def test_explicit_instance_type_bypasses_selection(self, flow_with_catalog):
        """Test that explicit instance_type bypasses capability selection."""
        flow, mock_provider, instances = flow_with_catalog

        # Explicitly request H100 (most expensive)
        config = TaskConfigBuilder() \
            .with_name("explicit-h100") \
            .with_instance_type("gpu.nvidia.h100") \
            .with_command("python benchmark.py") \
            .build()

        # Run the task
        task = flow.run(config)

        # Should use the explicit H100 despite it being most expensive
        submit_call = mock_provider.submit_task.call_args
        # Check instance_type is passed as keyword argument
        assert submit_call.kwargs['instance_type'] == "gpu.nvidia.h100"

    def test_empty_catalog_error(self, flow_with_catalog):
        """Test error handling when no instances are available."""
        flow, mock_provider, instances = flow_with_catalog

        with patch.object(flow, '_load_instance_catalog', return_value=[]):
            config_dict = {
                "name": "no-instances",
                "command": ["python", "train.py"],
                "min_gpu_memory_gb": 40
            }
            config = TaskConfig(**config_dict)

            # Should raise error about no instances
            with pytest.raises(ResourceNotAvailableError, match="No GPU instances found"):
                flow.run(config)


class TestInstanceTypeHandling:
    """Test various instance type formats and validation."""

    def test_instance_type_canonicalization(self):
        """Test that various instance type formats are handled."""
        # These should all be valid ways to specify instance types
        formats = [
            "a100",              # Short name
            "gpu.nvidia.a100",   # Full canonical
            "a100-80gb",         # With memory
            "8xa100",            # With count
            "a100.80gb.sxm4.1x", # Legacy format
        ]

        for fmt in formats:
            # Should not raise validation error
            config = TaskConfigBuilder() \
                .with_instance_type(fmt) \
                .build()
            assert config.instance_type == fmt

    def test_invalid_instance_type_format(self):
        """Test that invalid formats are caught during validation."""
        # This would be caught by provider during submission
        config = TaskConfigBuilder() \
            .with_instance_type("invalid-gpu-xyz") \
            .build()

        # Config creation succeeds (format validation happens at provider level)
        assert config.instance_type == "invalid-gpu-xyz"

    def test_min_gpu_memory_validation(self):
        """Test validation of min_gpu_memory_gb values."""
        # Valid range
        config = TaskConfig(
            name="test",
            command=["echo", "test"],
            min_gpu_memory_gb=80
        )
        assert config.min_gpu_memory_gb == 80

        # Test upper bound
        config = TaskConfig(
            name="test",
            command=["echo", "test"],
            min_gpu_memory_gb=640  # Max supported
        )
        assert config.min_gpu_memory_gb == 640

        # Test validation error for too high
        with pytest.raises(PydanticValidationError):
            TaskConfig(
                name="test",
                command=["echo", "test"],
                min_gpu_memory_gb=1000  # Too high
            )
