"""Behavior-focused unit tests for FCP provider.

These tests verify the provider's public API behavior without
testing implementation details or using excessive mocking.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.errors import APIError, TaskNotFoundError
from flow.providers.fcp.core.errors import (
    FCPInstanceError,
    FCPQuotaExceededError,
)
from flow.providers.fcp.provider import FCPProvider


class TestInstanceResolutionBehavior:
    """Test instance resolution from user's perspective."""

    @pytest.fixture
    def provider(self):
        """Provider with minimal test double."""
        config = Config(
            provider="fcp",
            auth_token="test",
            provider_config={"project": "test", "ssh_keys": ["key1"]}
        )

        # Simple test double that returns predictable responses
        http = Mock()
        http.request.return_value = []

        provider = FCPProvider(config, http_client=http)
        provider._project_id = "proj-123"  # Skip project resolution
        return provider, http

    def test_user_friendly_names_accepted(self, provider):
        """Users can use simple names like 'a100' everywhere."""
        provider, http = provider

        # All user-facing methods should accept friendly names
        user_friendly_names = ["a100", "2xa100", "8xh100", "h100"]

        for name in user_friendly_names:
            # find_instances should accept it
            try:
                provider.find_instances({"instance_type": name})
            except FCPInstanceError:
                pytest.fail(f"find_instances should accept '{name}'")

            # submit_task should accept it
            config = TaskConfig(name="test", instance_type=name, command=["echo"], upload_code=False)
            # Mock both availability check and bid creation
            def mock_request(method, url, **kwargs):
                if url == "/v2/spot/availability":
                    return [{
                        "fid": "auc_123",
                        "instance_type": provider._resolve_instance_type(name),
                        "region": "us-east-1",
                        "capacity": 10,
                        "last_instance_price": "$10.00"
                    }]
                elif url == "/v2/spot/bids":
                    return {"fid": "bid-123", "status": "pending"}
                return []

            http.request.side_effect = mock_request

            try:
                provider.submit_task(name, config)
            except FCPInstanceError:
                pytest.fail(f"submit_task should accept '{name}'")

    def test_helpful_errors_for_common_mistakes(self, provider):
        """Common user mistakes get helpful guidance."""
        provider, _ = provider

        common_mistakes = [
            "nvidia-a100",    # Vendor prefix
            "A100",          # Capitalization
            "gpu-a100",      # Wrong prefix
            "a100-gpu",      # Wrong suffix
            "a-100",         # Hyphenation
            "a100-80",       # Incomplete
        ]

        for mistake in common_mistakes:
            with pytest.raises(FCPInstanceError) as exc:
                provider.find_instances({"instance_type": mistake})

            error = str(exc.value)
            # Must provide guidance
            assert "Unknown instance type" in error
            assert mistake in error
            assert "Available:" in error
            # Should suggest valid options
            assert "a100" in error or "1xa100" in error

    def test_instance_type_consistency(self, provider):
        """Instance types are consistent across API calls."""
        provider, http = provider

        # Mock finding instances
        http.request.return_value = [{
            "fid": "auc-123",
            "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100 FID
            "last_instance_price": "$25.00",
            "region": "us-east-1"
        }]

        instances = provider.find_instances({"instance_type": "a100"})
        assert len(instances) == 1

        # The returned instance should show human-readable type
        assert instances[0].instance_type == "a100-80gb.sxm.1x"

        # When we use this to submit a task
        config = TaskConfig(
            name="test",
            instance_type="a100",  # User still uses simple name
            command=["echo"],
            upload_code=False  # Disable code upload to avoid large script
        )

        # Mock availability and bid creation
        def mock_request(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return [{
                    "fid": "auc-123",
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-east-1",
                    "capacity": 10,
                    "last_instance_price": "$25.00"
                }]
            elif url == "/v2/spot/bids":
                return {"fid": "bid-123", "status": "pending"}
            return []

        http.request.side_effect = mock_request
        task = provider.submit_task("a100", config)

        # The task should be created successfully
        assert task.task_id == "bid-123"


class TestTaskLifecycleBehavior:
    """Test task lifecycle from user's perspective."""

    @pytest.fixture
    def provider(self):
        """Provider with lifecycle test double."""
        config = Config(
            provider="fcp",
            auth_token="test",
            provider_config={"project": "test"}
        )

        class LifecycleTestDouble:
            def __init__(self):
                self.tasks = {}

            def request(self, method, url, **kwargs):
                if url == "/v2/spot/availability":
                    # Return availability for a100
                    return [{
                        "fid": "auc-123",
                        "instance_type": "it_MsIRhxj3ccyVWGfP",
                        "region": "us-east-1",
                        "capacity": 10,
                        "last_instance_price": "$10.00"
                    }]
                elif url == "/v2/spot/bids" and method == "POST":
                    bid_id = f"bid-{len(self.tasks) + 1}"
                    self.tasks[bid_id] = {
                        "fid": bid_id,
                        "status": "pending",
                        "name": kwargs["json"]["name"],
                        "created_at": datetime.now().isoformat(),
                    }
                    return self.tasks[bid_id]

                elif url == "/v2/spot/bids" and method == "GET":
                    # Progress tasks and return all
                    for task in self.tasks.values():
                        if task["status"] == "pending":
                            task["status"] = "provisioning"
                        elif task["status"] == "provisioning":
                            task["status"] = "allocated"
                    return list(self.tasks.values())

                elif url.startswith("/v2/spot/bids/bid-"):
                    bid_id = url.split("/")[-1]
                    if bid_id in self.tasks:
                        # Progress the status
                        task = self.tasks[bid_id]
                        if task["status"] == "pending":
                            task["status"] = "provisioning"
                        elif task["status"] == "provisioning":
                            task["status"] = "allocated"
                        return task

                return []

        http = LifecycleTestDouble()
        provider = FCPProvider(config, http_client=http)
        provider._project_id = "proj-123"
        return provider, http

    def test_task_progresses_through_states(self, provider):
        """Tasks progress through expected lifecycle states."""
        provider, http = provider

        # Submit task
        config = TaskConfig(
            name="lifecycle-test",
            instance_type="a100",
            command=["python", "train.py"],
            upload_code=False  # Disable code upload to avoid large script
        )

        task = provider.submit_task("a100", config)
        assert task.status == TaskStatus.PENDING

        # Check status - should progress
        task2 = provider.get_task(task.task_id)
        assert task2.status == TaskStatus.PENDING  # Now provisioning

        # Check again - should be running
        task3 = provider.get_task(task.task_id)
        assert task3.status == TaskStatus.RUNNING  # Now allocated

    def test_task_not_found_behavior(self, provider):
        """Missing tasks raise appropriate errors."""
        provider, _ = provider

        with pytest.raises(TaskNotFoundError) as exc:
            provider.get_task("bid-nonexistent")

        assert "bid-nonexistent" in str(exc.value)


class TestErrorHandlingBehavior:
    """Test error handling from user's perspective."""

    @pytest.fixture
    def provider(self):
        """Provider that can simulate various errors."""
        config = Config(
            provider="fcp",
            auth_token="test",
            provider_config={"project": "test"}
        )

        http = Mock()
        provider = FCPProvider(config, http_client=http)
        provider._project_id = "proj-123"
        return provider, http

    def test_quota_exceeded_error(self, provider):
        """Quota errors are clearly communicated."""
        provider, http = provider

        # Simulate quota error
        http.request.side_effect = APIError(
            "GPU quota exceeded for project",
            status_code=429
        )

        with pytest.raises(FCPQuotaExceededError) as exc:
            provider.find_instances({"instance_type": "a100"})

        assert "quota exceeded" in str(exc.value).lower()

    def test_network_error_handling(self, provider):
        """Network errors are handled gracefully."""
        provider, http = provider

        # Simulate network error
        http.request.side_effect = ConnectionError("Network is unreachable")

        with pytest.raises(Exception) as exc:
            provider.find_instances({"instance_type": "a100"})

        # Should bubble up as a clear error
        assert "Network" in str(exc.value)

    def test_invalid_auction_id(self, provider):
        """Invalid instance types give clear errors."""
        provider, http = provider

        config = TaskConfig(name="test", instance_type="invalid-gpu", command=["echo"])

        with pytest.raises(FCPInstanceError) as exc:
            provider.submit_task("invalid-gpu", config)

        assert "invalid-gpu" in str(exc.value)
        assert "Unknown instance type" in str(exc.value)


class TestProviderCapabilities:
    """Test what capabilities the provider exposes."""

    def test_provider_interface(self):
        """Provider implements expected interface."""
        config = Config(
            provider="fcp",
            auth_token="test",
            provider_config={"project": "test"}
        )

        provider = FCPProvider(config, http_client=Mock())

        # Should have these methods
        assert hasattr(provider, 'find_instances')
        assert hasattr(provider, 'submit_task')
        assert hasattr(provider, 'get_task')
        assert hasattr(provider, 'terminate_task')
        assert hasattr(provider, 'get_logs')

        # Should be callable
        assert callable(provider.find_instances)
        assert callable(provider.submit_task)

    def test_instance_type_discovery(self):
        """Users can discover available instance types."""
        config = Config(
            provider="fcp",
            auth_token="test",
            provider_config={"project": "test"}
        )

        http = Mock()
        provider = FCPProvider(config, http_client=http)

        # Provider should have some way to discover instance types
        # Even if it's just through error messages
        with pytest.raises(FCPInstanceError) as exc:
            provider.find_instances({"instance_type": "invalid"})

        error = str(exc.value)
        # Should list available types
        assert "Available:" in error
        assert "a100" in error
        assert "h100" in error
