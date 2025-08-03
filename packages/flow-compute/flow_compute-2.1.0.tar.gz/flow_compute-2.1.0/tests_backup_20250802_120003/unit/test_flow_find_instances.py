"""Test Flow.find_instances method."""

from unittest.mock import Mock

from flow import Flow
from flow._internal.config import Config


class TestFlowFindInstances:
    """Test the Flow.find_instances method."""

    def test_find_instances_basic(self):
        """Test basic find_instances functionality."""
        # Create mock provider
        mock_provider = Mock()
        mock_provider.find_instances.return_value = [
            {"instance_type": "a100", "price_per_hour": 2.50, "gpu_count": 1},
            {"instance_type": "h100", "price_per_hour": 4.50, "gpu_count": 1},
        ]

        # Create Flow instance with mocked config
        mock_config = Mock(spec=Config)
        flow = Flow(config=mock_config)
        flow._provider = mock_provider

        # Call find_instances
        requirements = {"gpu_type": "a100", "max_price": 10.0}
        instances = flow.find_instances(requirements, limit=5)

        # Verify provider method was called correctly
        mock_provider.find_instances.assert_called_once_with(requirements, limit=5)

        # Verify results
        assert len(instances) == 2
        assert instances[0]["instance_type"] == "a100"
        assert instances[1]["instance_type"] == "h100"

    def test_find_instances_empty_results(self):
        """Test find_instances with no matching results."""
        mock_provider = Mock()
        mock_provider.find_instances.return_value = []

        mock_config = Mock(spec=Config)
        flow = Flow(config=mock_config)
        flow._provider = mock_provider

        instances = flow.find_instances({"gpu_type": "impossible"})

        assert instances == []
        mock_provider.find_instances.assert_called_once()

    def test_find_instances_with_filters(self):
        """Test find_instances with various filter combinations."""
        mock_provider = Mock()
        mock_provider.find_instances.return_value = [
            {
                "instance_type": "8xa100",
                "price_per_hour": 16.0,
                "gpu_count": 8,
                "gpu_memory_gb": 80,
                "region": "us-east-1"
            }
        ]

        mock_config = Mock(spec=Config)
        flow = Flow(config=mock_config)
        flow._provider = mock_provider

        requirements = {
            "instance_type": "8xa100",
            "max_price": 20.0,
            "region": "us-east-1",
            "min_gpu_count": 8
        }

        instances = flow.find_instances(requirements, limit=10)

        # Verify filtering worked
        assert len(instances) == 1
        assert instances[0]["gpu_count"] == 8
        assert instances[0]["price_per_hour"] <= 20.0

    def test_find_instances_explicit_usage(self):
        """Test that find_instances requires explicit Flow instance creation."""
        # This test documents the intended usage pattern: explicit is better than implicit
        mock_provider = Mock()
        mock_provider.find_instances.return_value = [
            {"instance_type": "a100", "price_per_hour": 3.0}
        ]

        mock_flow = Flow(config=Config(provider="test", auth_token="test"))
        mock_flow._provider = mock_provider

        # The correct way to use find_instances - explicitly through a Flow instance
        instances = mock_flow.find_instances({"gpu_type": "a100"})

        # Verify it was called
        assert len(instances) == 1
        assert instances[0]["instance_type"] == "a100"

    def test_find_instances_provider_not_initialized(self):
        """Test find_instances when provider hasn't been initialized."""
        mock_config = Mock(spec=Config)
        flow = Flow(config=mock_config)

        # Mock _ensure_provider to return a mock provider
        mock_provider = Mock()
        mock_provider.find_instances.return_value = []

        flow._ensure_provider = Mock(return_value=mock_provider)

        # Should work even without explicit provider initialization
        instances = flow.find_instances({"gpu_type": "a100"})

        flow._ensure_provider.assert_called_once()
        assert instances == []
