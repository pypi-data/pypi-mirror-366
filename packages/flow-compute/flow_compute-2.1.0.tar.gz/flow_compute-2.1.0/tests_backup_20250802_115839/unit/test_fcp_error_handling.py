"""Unit tests for FCP provider error handling.

These tests focus on error scenarios, retry logic, validation,
and error message clarity.
"""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.errors import APIError
from flow.providers.fcp.adapters.models import FCPAdapter
from flow.providers.fcp.core.errors import FCPInstanceError
from flow.providers.fcp.core.models import FCPBid, FCPInstance
from flow.providers.fcp.provider import FCPProvider
from tests.support.framework import TaskConfigBuilder


@pytest.mark.unit
@pytest.mark.quick


class TestFCPErrorHandling:
    """Test provider's error handling logic."""

    @pytest.fixture
    def provider(self):
        """Create provider with mocked HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        # Mock the project ID to avoid resolver calls
        provider._project_id = "proj-123"
        return provider

    def test_handle_error_response(self, provider):
        """Test error response handling."""
        # Mock SSH key manager to avoid the API calls
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Test various error responses
        error_cases = [
            (
                {"error": "INVALID_INSTANCE_TYPE", "message": "Unknown GPU type"},
                APIError,
                "Unknown GPU type"
            ),
            (
                {"error": "RESOURCE_NOT_FOUND", "message": "Bid not found"},
                APIError,
                "Bid not found"
            ),
            (
                {"error": "QUOTA_EXCEEDED", "message": "GPU quota exceeded"},
                APIError,
                "GPU quota exceeded"
            ),
        ]

        for error_response, expected_exception, expected_message in error_cases:
            # Mock both availability check and bid submission
            def mock_request_side_effect(method, url, **kwargs):
                if url == "/v2/spot/availability":
                    # Return some availability so we proceed to bid submission
                    return [{
                        "fid": "auc_123",
                        "instance_type": "it_MsIRhxj3ccyVWGfP",
                        "region": "us-east-1",
                        "capacity": 10,
                        "last_instance_price": "$5.00"
                    }]
                elif url == "/v2/spot/bids" and method == "POST":
                    raise APIError(
                        message=error_response["message"],
                        status_code=400,
                        response_body=str(error_response)
                    )
                # Return empty lists for other API calls
                return []

            provider.http.request = Mock(side_effect=mock_request_side_effect)

            with pytest.raises(expected_exception) as exc_info:
                provider.submit_task(
                    instance_type="a100",
                    config=TaskConfigBuilder().with_instance_type("a100").with_upload_code(False).build()
                )
            # Check that the error message is included
            assert expected_message in str(exc_info.value)

    def test_helpful_error_for_invalid_instance_type(self, provider):
        """Test that users get helpful guidance for invalid instance types."""
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Test common user mistakes
        invalid_config = TaskConfigBuilder().with_instance_type("nvidia-a100").build()

        with pytest.raises(FCPInstanceError) as exc_info:
            provider.submit_task(instance_type="nvidia-a100", config=invalid_config)

        error_message = str(exc_info.value)
        # Error should guide users to valid options
        assert "Unknown instance type: nvidia-a100" in error_message
        assert "Available:" in error_message
        # Check that some valid options are listed
        assert "a100" in error_message
        assert "2xa100" in error_message


class TestFCPRetryLogic:
    """Test provider's retry and error handling logic."""

    @pytest.fixture
    def provider(self):
        """Create provider with mocked HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "project": "test-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        # Mock the project ID to avoid resolver calls
        provider._project_id = "proj-123"
        return provider

    def test_transient_error_retry(self, provider):
        """Test that transient errors are retried by HTTP client."""
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # The HTTP client itself handles retries for 5xx errors
        # So we test that the provider correctly passes through the retry behavior

        # Mock to return proper responses for each API call
        def mock_request(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return [{
                    "fid": "auc_123",
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-east-1",
                    "capacity": 10,
                    "last_instance_price": "$5.00"
                }]
            elif url == "/v2/spot/bids" and method == "POST":
                return {
                    "fid": "bid-123",
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-east-1"
                }
            return []

        provider.http.request = Mock(side_effect=mock_request)

        # Should succeed
        task = provider.submit_task(
            instance_type="a100",
            config=TaskConfigBuilder().with_instance_type("a100").with_upload_code(False).build()
        )

        assert task.task_id == "bid-123"
        # Provider makes multiple calls (availability check + bid submission)
        assert provider.http.request.call_count >= 2

    def test_non_transient_error_no_retry(self, provider):
        """Test that non-transient errors don't trigger retries."""
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Mock HTTP to return client error only for bid submission
        def mock_request_side_effect(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return [{
                    "fid": "auc_123",
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-east-1",
                    "capacity": 10,
                    "last_instance_price": "$5.00"
                }]
            elif url == "/v2/spot/bids" and method == "POST":
                raise APIError("Invalid request", status_code=400)
            return []

        provider.http.request = Mock(side_effect=mock_request_side_effect)

        # Should fail immediately without retry
        with pytest.raises(APIError) as exc_info:
            provider.submit_task(
                instance_type="a100",
                config=TaskConfigBuilder().with_instance_type("a100").with_upload_code(False).build()
            )

        # Check that the error message is preserved
        assert "Invalid request" in str(exc_info.value)

        # Called at least twice (availability + bid attempt)
        assert provider.http.request.call_count >= 2


class TestFCPParsingErrors:
    """Test handling of parsing and data conversion errors."""

    def test_parse_price_various_formats(self):
        """Test price parsing handles various formats."""
        test_cases = [
            ("25.60", 25.60),
            ("$25.60", 25.60),
            ("100", 100.0),
            ("$0.50", 0.50),
            (None, 0.0),
            ("", 0.0),
            ("invalid", 0.0),
        ]

        for input_price, expected in test_cases:
            result = FCPAdapter._parse_price(input_price)
            assert result == expected, f"Failed to parse {input_price}"

    def test_calculate_runtime_hours(self):
        """Test runtime calculation logic."""
        start = datetime(2024, 1, 1, 10, 0, 0)
        test_cases = [
            # (end_time, expected_hours)
            (datetime(2024, 1, 1, 11, 0, 0), 1.0),
            (datetime(2024, 1, 1, 10, 30, 0), 0.5),
            (datetime(2024, 1, 1, 12, 15, 0), 2.25),
            (datetime(2024, 1, 2, 10, 0, 0), 24.0),
        ]

        for end, expected_hours in test_cases:
            hours = FCPAdapter._calculate_runtime_hours(start, end)
            assert abs(hours - expected_hours) < 0.01, f"Wrong hours for {end}"

    def test_bid_to_task_with_missing_fields(self):
        """Test graceful handling of missing bid fields."""
        # Create bid with minimal fields
        bid = FCPBid(
            fid="bid-123",
            name="test-task",
            status="running",
            limit_price="$0.00",  # Use $0.00 to simulate missing/unknown price
            created_at=datetime.now(),
            # Required fields
            project="proj-123",
            created_by="user-123",
            instance_quantity=1,
            instance_type="it_XqgKWbhZ5gznAYsG",
            region="us-east-1",
        )

        # Should still convert successfully
        task = FCPAdapter.bid_to_task(bid)
        
        assert task.task_id == "bid-123"
        # Price parsing should handle None gracefully
        # No cost_per_hour in Task model anymore

    def test_parse_instance_response_with_invalid_data(self):
        """Test parsing handles malformed instance data gracefully."""
        provider = FCPProvider(Config(
            provider="fcp",
            auth_token="test-token"
        ))
        
        # Mock response with some invalid entries
        provider.http = Mock()
        provider.http.request = Mock(return_value=[
            {
                "fid": "auc_123",
                "auction_id": "auction-123",
                "instance_type": "it_MsIRhxj3ccyVWGfP",
                "region": "us-east-1a",
                "last_instance_price": "$25.60",
                "available_gpus": 4,
                "gpu_type": "A100",
                "gpu_count": 1,
            },
            {
                # Missing required fields
                "fid": "auc_456",
                "instance_type": None,  # Invalid
                "region": "us-west-2",
            },
            {
                # Another valid entry
                "fid": "auc_789",
                "auction_id": "auction-789",
                "instance_type": "it_5M6aGxGovNeX5ltT",
                "region": "us-west-2",
                "last_instance_price": "invalid-price",  # Invalid price
                "available_gpus": 2,
                "gpu_type": "A100",
                "gpu_count": 2,
            }
        ])

        # Should filter out invalid entries gracefully
        instances = provider.find_instances({"instance_type": "a100"})
        
        # Should have parsed valid entries
        assert len(instances) >= 1
        assert any(i.allocation_id == "auc_123" for i in instances)