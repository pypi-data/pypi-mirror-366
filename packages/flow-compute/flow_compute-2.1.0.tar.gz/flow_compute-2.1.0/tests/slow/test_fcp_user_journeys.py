"""Integration tests for FCP user journeys with instance resolution.

These tests verify the complete flow from user-friendly instance names
to successful API calls and task creation.
"""

from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig
from flow.providers.fcp.provider import FCPProvider


class TestFCPUserJourneys:
    """Test real user workflows with instance resolution.
    
    We mock ONLY the HTTP boundary - everything else runs real code.
    """

    def _setup_provider_test_state(self, provider):
        """Set up provider state for testing without external calls."""
        # This is a test-specific setup to avoid external API calls
        # In production, these would be resolved via API
        provider._project_id = "proj-123"
        provider.ssh_key_manager._project_id = "proj-123"

    @pytest.fixture
    def provider(self):
        """Create FCP provider with mocked HTTP client only."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "project": "test-project",
                "region": "us-central1-a",
                "ssh_keys": ["test-key"],  # Provide SSH keys in config
            }
        )
        mock_http = Mock()
        # Mock project resolution at HTTP level
        mock_http.request = Mock(side_effect=self._mock_http_request)
        provider = FCPProvider(config, http_client=mock_http)
        provider._http_mock = mock_http  # Store for assertions
        # Set up provider state to avoid external calls
        self._setup_provider_test_state(provider)
        return provider

    def _mock_http_request(self, method, url, **kwargs):
        """Mock HTTP responses based on URL."""
        if url == "/v2/projects":
            return [{"fid": "proj-123", "name": "test-project", "created_at": "2024-01-01T00:00:00Z"}]
        elif url == "/v2/ssh-keys":
            return [{"fid": "ssh-key-123", "name": "test-key", "public_key": "ssh-rsa ..."}]
        elif url == "/v2/spot/bids" and method == "POST":
            return {"fid": "bid_123", "status": "pending"}
        elif url == "/v2/spot/availability":
            # Return mock availability with proper FCP instance type FIDs
            return [{
                "fid": "auc_123",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100 FID
                "last_instance_price": "$25.00",
                "region": "us-central1-a",
                "capacity": 5,
            }]
        return []

    def test_submit_job_with_friendly_instance_name(self, provider):
        """Test that users can use 'a100' instead of FCP's internal ID."""
        # What users actually do
        config = TaskConfig(
            name="my-training",
            instance_type="a100",  # Simple name
            command=["python", "train.py"],
            upload_code=False,  # Disable code upload for integration test
        )

        # Submit task with user-friendly instance type
        task = provider.submit_task("a100", config)

        # Task should be created
        assert task.task_id == "bid_123"

        # Find the bid creation call in our mock
        bid_calls = [call for call in provider._http_mock.request.call_args_list
                     if "url" in call.kwargs and call.kwargs["url"] == "/v2/spot/bids"
                     and call.kwargs.get("method") == "POST"]
        assert len(bid_calls) == 1

        # Verify FCP received the correct FID, not "a100"
        bid_payload = bid_calls[0].kwargs["json"]
        assert bid_payload["instance_type"] == "it_MsIRhxj3ccyVWGfP"

    def test_find_instances_with_count_prefix_format(self, provider):
        """Test finding instances using count prefix format (e.g., 8xa100)."""
        # Mock API response with FCP FIDs
        provider.http.request = Mock(return_value=[
            {
                "fid": "auc_abc123",
                "instance_type": "it_J7OyNf9idfImLIFo",  # FID for 8xa100
                "region": "us-central1-a",
                "last_instance_price": "$80.00",
                "capacity": 2,
            }
        ])

        # User searches with friendly format
        instances = provider.find_instances({
            "instance_type": "8xa100",
            "region": "us-central1-a",
        })

        # Verify API was called with correct FID
        provider.http.request.assert_called_with(
            method="GET",
            url="/v2/spot/availability",
            params={
                "limit": "10",
                "instance_type": "it_J7OyNf9idfImLIFo",
                "region": "us-central1-a",
            }
        )

        # Verify response shows human-readable name
        assert len(instances) == 1
        assert instances[0].instance_type == "a100-80gb.sxm.8x"
        assert instances[0].price_per_hour == 80.0

    def test_error_guidance_for_common_mistakes(self, provider):
        """Test that common user mistakes get helpful error messages."""
        # Mock SSH keys
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["ssh-key-123"])

        # Common mistakes users might make
        mistake_configs = [
            ("nvidia-a100", "vendor-prefix"),
            ("A100", "capitalization"),
            ("gpu-a100", "wrong-prefix"),
            ("a100-gpu", "wrong-suffix"),
        ]

        for mistake, reason in mistake_configs:
            config = TaskConfig(
                name=f"test-{reason}",
                instance_type=mistake,
                command=["echo", "test"],
            )

            with pytest.raises(Exception) as exc_info:
                provider.submit_task("auc_123", config)

            error = str(exc_info.value)
            # Should provide available options
            assert "Available:" in error, f"No guidance for {reason}: {mistake}"
            assert "a100" in error, f"Missing valid option in error for: {mistake}"

    def test_h100_instance_resolution(self, provider):
        """Test H100 instance type resolution."""
        # Update mock to return h100 availability and bid
        def mock_h100_request(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return [{
                    "fid": "auc_h100",
                    "instance_type": "it_5ECSoHQjLBzrp5YM",  # h100 FID
                    "last_instance_price": "$50.00",
                    "region": "us-central1-a",
                    "capacity": 2,
                }]
            elif url == "/v2/spot/bids" and method == "POST":
                return {"fid": "bid_789", "status": "pending"}
            elif url == "/v2/ssh-keys":
                return [{"fid": "ssh-key-123", "name": "test-key", "public_key": "ssh-rsa ..."}]
            return []

        provider.http.request = Mock(side_effect=mock_h100_request)

        # Test both H100 formats
        for instance_type in ["8xh100", "h100-80gb.sxm.8x"]:
            config = TaskConfig(
                name="h100-test",
                instance_type=instance_type,
                command=["nvidia-smi"],
                upload_code=False,  # Disable code upload for integration test
            )

            task = provider.submit_task(instance_type, config)
            assert task.task_id == "bid_789"

            # Verify correct FID was used
            call_args = provider.http.request.call_args
            bid_payload = call_args[1]["json"]
            assert bid_payload["instance_type"] == "it_5ECSoHQjLBzrp5YM"
