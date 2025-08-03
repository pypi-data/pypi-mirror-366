"""Test FCP instance resolution behavior.

These tests verify that user-friendly instance names work correctly
throughout the system. We test behavior, not implementation.
"""

from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig
from flow.providers.fcp.core.errors import FCPInstanceError
from flow.providers.fcp.provider import FCPProvider


class TestInstanceResolutionBehavior:
    """Test that instance resolution works for users."""

    @pytest.fixture
    def provider(self):
        """Create provider with minimal mocking."""
        config = Config(
            provider="fcp",
            auth_token="test",
            provider_config={"project": "test-proj", "ssh_keys": ["key1"]}
        )
        # Only mock HTTP - the one external dependency
        http_mock = Mock()
        provider = FCPProvider(config, http_client=http_mock)
        provider._project_id = "proj-123"  # Skip project resolution
        return provider, http_mock

    def test_find_instances_accepts_user_friendly_names(self, provider):
        """Test that find_instances works with names like 'a100'."""
        provider, http_mock = provider

        # Mock API response
        http_mock.request.return_value = [{
            "fid": "auc_123",
            "instance_type": "it_MsIRhgM4LFznrZE3",
            "last_instance_price": "$25.00",
            "region": "us-east-1",
            "capacity": 10
        }]

        # User calls with friendly name
        instances = provider.find_instances({"instance_type": "a100"})

        # Should work and return results
        assert len(instances) == 1
        assert instances[0].price_per_hour == 25.0

        # API should have received the FID
        # Find the spot availability call
        spot_calls = [call for call in http_mock.request.call_args_list
                      if len(call) >= 2 and "url" in call[1] and "/spot/availability" in call[1]["url"]]
        assert len(spot_calls) == 1

        call_params = spot_calls[0][1]["params"]
        assert call_params["instance_type"] == "it_MsIRhxj3ccyVWGfP"

    def test_invalid_instance_type_gives_helpful_error(self, provider):
        """Test error message guides users to valid options."""
        provider, http_mock = provider

        # User tries invalid type
        with pytest.raises(FCPInstanceError) as exc:
            provider.find_instances({"instance_type": "nvidia-a100"})

        error = str(exc.value)
        # Must list valid options
        assert "Unknown instance type: nvidia-a100" in error
        assert "Available:" in error
        assert "a100" in error  # Should suggest this
        assert "2xa100" in error
        assert "8xa100" in error

    def test_all_supported_formats_work(self, provider):
        """Test all documented instance formats work."""
        provider, http_mock = provider

        # Set up mock to return success
        http_mock.request.return_value = [{
            "fid": "auc_123",
            "instance_type": "it_xxx",
            "last_instance_price": "$10.00",
            "region": "us-east-1"
        }]

        # All these should work without error
        supported_formats = [
            "a100",                  # Simple
            "2xa100",               # Count prefix
            "a100-80gb.sxm.1x",     # FCP format
            "8xh100",               # H100
            "it_MsIRhgM4LFznrZE3",  # Direct FID
        ]

        for fmt in supported_formats:
            # Reset mock
            http_mock.request.reset_mock()

            # Should not raise
            instances = provider.find_instances({"instance_type": fmt})
            assert len(instances) == 1

            # Verify a call was made
            assert http_mock.request.called, f"No API call for format: {fmt}"

    def test_submit_task_resolves_instance_type(self, provider):
        """Test submit_task works with user-friendly names."""
        provider, http_mock = provider

        # Mock availability and bid creation
        def mock_request(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return [{
                    "fid": "auc_123",
                    "instance_type": "it_fK7Cx6TVhOK5ZfXT",  # 4xa100 FID
                    "region": "us-east-1",
                    "capacity": 10,
                    "last_instance_price": "$10.00"
                }]
            elif url == "/v2/spot/bids":
                return {"fid": "bid_123", "status": "pending"}
            return []

        http_mock.request.side_effect = mock_request

        # User submits with friendly name
        config = TaskConfig(
            name="test",
            instance_type="4xa100",
            command=["echo", "test"],
            upload_code=False
        )

        task = provider.submit_task("4xa100", config)
        assert task.task_id == "bid_123"

        # Find the bid creation call
        bid_calls = [c for c in http_mock.request.call_args_list
                     if len(c) >= 2 and "url" in c[1] and c[1]["url"] == "/v2/spot/bids"]
        assert len(bid_calls) == 1, "Should have made exactly one bid creation call"

        # Should use correct FID
        payload = bid_calls[0][1]["json"]
        assert payload["instance_type"] == "it_fK7Cx6TVhOK5ZfXT"  # 4xa100 FID
