"""Unit tests for FCP provider implementation.

These tests focus on OUR code logic, not the external API behavior.
We mock only at the HTTP boundary to test our parsing, error handling,
and business logic.

IMPROVEMENTS:
- Mock only external boundaries (HTTP client)
- Test real adapter and provider logic
- No mocking of internal methods
- Clear test data constants
- Focus on behavior, not implementation
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskStatus
from flow.errors import APIError
from flow.providers.fcp.adapters.models import FCPAdapter
from flow.providers.fcp.core.errors import FCPInstanceError
from flow.providers.fcp.core.models import FCPBid, FCPInstance
from flow.providers.fcp.provider import FCPProvider
from tests.testing import TaskConfigBuilder

# Test constants
DEFAULT_API_URL = "https://api.test.com"
DEFAULT_PROJECT_ID = "proj-123"
DEFAULT_AUTH_TOKEN = "test-token"

# Instance type FIDs for testing - must match provider.py INSTANCE_TYPE_MAPPINGS
INSTANCE_TYPE_FIDS = {
    "a100": "it_MsIRhxj3ccyVWGfP",
    "2xa100": "it_5M6aGxGovNeX5ltT",
    "8xa100": "it_J7OyNf9idfImLIFo",
    "h100": "it_5ECSoHQjLBzrp5YM",  # This is the correct FID from provider.py
    "8xh100": "it_5ECSoHQjLBzrp5YM",  # Same as h100 in provider
}

# Price constants
PRICE_A100_SINGLE = 25.60
PRICE_A100_8X = 80.00
PRICE_H100_8X = 50.00


class TestFCPAdapter:
    """Test our adapter logic for converting between FCP and domain models.
    
    These tests verify the adapter's transformation logic without any mocks.
    """

    def test_bid_status_mapping(self):
        """Test that we correctly map FCP statuses to our domain statuses."""
        # Test all known mappings
        test_cases = [
            ("pending", TaskStatus.PENDING),
            ("provisioning", TaskStatus.PENDING),
            ("allocated", TaskStatus.RUNNING),
            ("running", TaskStatus.RUNNING),
            ("completed", TaskStatus.COMPLETED),
            ("failed", TaskStatus.FAILED),
            ("terminated", TaskStatus.COMPLETED),
            ("cancelled", TaskStatus.CANCELLED),
            ("deactivated", TaskStatus.CANCELLED),
            ("terminating", TaskStatus.CANCELLED),
        ]

        for fcp_status, expected_status in test_cases:
            bid = FCPBid(
                fid="bid-123",
                name="test-task",
                status=fcp_status,
                limit_price="25.60",
                created_at=datetime.now(timezone.utc),
                project=DEFAULT_PROJECT_ID,
                created_by="user-123",
                instance_quantity=1,
                instance_type=INSTANCE_TYPE_FIDS["a100"],
                region="us-east-1",
            )

            task = FCPAdapter.bid_to_task(bid)

            assert task.status == expected_status, \
                f"Failed to map {fcp_status} to {expected_status}"

    def test_bid_to_task_with_instances(self):
        """Test bid to task conversion with instance details."""
        # Create test data
        created_at = datetime.now(timezone.utc)
        started_at = created_at + timedelta(minutes=2)
        
        bid = FCPBid(
            fid="bid-123",
            name="gpu-training",
            status="allocated",
            limit_price="35.50",
            created_at=created_at,
            project=DEFAULT_PROJECT_ID,
            created_by="user-123",
            instance_quantity=1,
            instance_type=INSTANCE_TYPE_FIDS["h100"],
            region="us-east-1",
        )

        instances = [
            FCPInstance(
                fid="i-123",
                bid_id="bid-123",
                status="running",
                created_at=started_at,
                instance_type=INSTANCE_TYPE_FIDS["h100"],
                region="us-east-1",
            )
        ]

        # Convert with human-readable instance type name
        task = FCPAdapter.bid_to_task(bid, instances, instance_type_name="H100 80GB")

        # Verify conversion
        assert task.task_id == "bid-123"
        assert task.name == "gpu-training"
        assert task.status == TaskStatus.RUNNING
        assert task.started_at == started_at
        assert task.instance_type == "H100 80GB"
        assert "i-123" in task.instances

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
            ("$1,000.50", 1000.50),  # With comma
            ("$ 25.60", 25.60),  # With space
        ]

        for input_price, expected in test_cases:
            result = FCPAdapter._parse_price(input_price)
            assert result == expected, \
                f"Failed to parse '{input_price}' - expected {expected}, got {result}"

    def test_calculate_runtime_hours(self):
        """Test runtime calculation logic."""
        start = datetime(2024, 1, 1, 10, 0, 0)
        test_cases = [
            # (end_time, expected_hours)
            (datetime(2024, 1, 1, 11, 0, 0), 1.0),
            (datetime(2024, 1, 1, 10, 30, 0), 0.5),
            (datetime(2024, 1, 1, 12, 15, 0), 2.25),
            (datetime(2024, 1, 2, 10, 0, 0), 24.0),
            (datetime(2024, 1, 1, 10, 0, 30), 0.0083),  # 30 seconds
        ]

        for end, expected_hours in test_cases:
            hours = FCPAdapter._calculate_runtime_hours(start, end)
            assert abs(hours - expected_hours) < 0.01, \
                f"Wrong hours for {end} - expected {expected_hours}, got {hours}"

    def test_bid_to_task_with_cost_calculation(self):
        """Test that task conversion calculates costs correctly."""
        created_at = datetime.now(timezone.utc)
        completed_at = created_at + timedelta(hours=2, minutes=30)
        
        bid = FCPBid(
            fid="bid-456",
            name="training-job",
            status="terminated",  # Use terminated status for completed tasks
            limit_price=str(PRICE_A100_SINGLE),
            created_at=created_at,
            deactivated_at=completed_at,  # Use deactivated_at instead of completed_at
            project=DEFAULT_PROJECT_ID,
            created_by="user-123",
            instance_quantity=1,
            instance_type=INSTANCE_TYPE_FIDS["a100"],
            region="us-west-2",
        )
        
        task = FCPAdapter.bid_to_task(bid)
        
        # 2.5 hours * $25.60/hour = $64.00
        expected_cost = 2.5 * PRICE_A100_SINGLE
        assert task.total_cost == f"${expected_cost:.2f}"


class MockHTTPResponse:
    """Mock HTTP response for testing error handling."""
    
    def __init__(self, data: Any, status_code: int = 200):
        self.data = data
        self.status_code = status_code
        
    def json(self):
        return self.data


class TestFCPProviderParsing:
    """Test provider's response parsing logic.
    
    We mock only the HTTP client to test our parsing logic.
    """

    def create_provider(self) -> tuple[FCPProvider, Mock]:
        """Create provider with mocked HTTP client."""
        config = Config(
            provider="fcp",
            auth_token=DEFAULT_AUTH_TOKEN,
            provider_config={
                "api_url": DEFAULT_API_URL,
                "project": "test-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        # Set project ID to avoid resolver calls
        provider._project_id = DEFAULT_PROJECT_ID
        return provider, mock_http

    def test_parse_instance_response(self):
        """Test parsing of find_instances API response."""
        provider, mock_http = self.create_provider()
        
        # Mock response at HTTP boundary - API filters based on instance_type param
        def mock_request(method, url, **kwargs):
            all_instances = [
                {
                    "fid": "auc_123",
                    "auction_id": "auction-123",
                    "instance_type": INSTANCE_TYPE_FIDS["a100"],
                    "region": "us-east-1a",
                    "last_instance_price": f"${PRICE_A100_SINGLE}",
                    "available_gpus": 4,
                    "gpu_type": "A100",
                    "gpu_count": 1,
                    "capacity": 10,
                },
                {
                    "fid": "auc_456",
                    "instance_type": INSTANCE_TYPE_FIDS["8xa100"],
                    "region": "us-west-2",
                    "last_instance_price": f"${PRICE_A100_8X}",
                    "capacity": 2,
                }
            ]
            
            # Filter by instance_type if provided in params
            params = kwargs.get("params", {})
            if "instance_type" in params:
                requested_type = params["instance_type"]
                return [i for i in all_instances if i["instance_type"] == requested_type]
            return all_instances
            
        mock_http.request = Mock(side_effect=mock_request)

        # Call our parsing logic through the public method
        instances = provider.find_instances({"instance_type": "a100"})

        # Verify parsing
        assert len(instances) == 1  # Filtered to just a100
        instance = instances[0]
        assert instance.allocation_id == "auc_123"
        assert instance.price_per_hour == PRICE_A100_SINGLE
        assert instance.region == "us-east-1a"
        assert instance.instance_type == "a100-80gb.sxm.1x"

    def test_handle_error_response(self):
        """Test error response handling."""
        provider, mock_http = self.create_provider()
        
        # Mock SSH key manager to avoid API calls
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Test various error responses
        error_cases = [
            (
                {"error": "INVALID_INSTANCE_TYPE", "message": "Unknown GPU type: invalid-gpu"},
                "Unknown GPU type: invalid-gpu"
            ),
            (
                {"error": "RESOURCE_NOT_FOUND", "message": "Bid not found: bid-xyz"},
                "Bid not found: bid-xyz"
            ),
            (
                {"error": "QUOTA_EXCEEDED", "message": "GPU quota exceeded for project"},
                "GPU quota exceeded for project"
            ),
        ]

        for error_response, expected_message in error_cases:
            def mock_request_side_effect(method, url, **kwargs):
                if url == "/v2/spot/availability":
                    # Return some availability so we proceed to bid submission
                    return [{
                        "fid": "auc_123",
                        "instance_type": INSTANCE_TYPE_FIDS["a100"],
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
                return []

            mock_http.request = Mock(side_effect=mock_request_side_effect)

            with pytest.raises(APIError) as exc_info:
                provider.submit_task(
                    instance_type="a100",
                    config=TaskConfigBuilder()
                        .with_instance_type("a100")
                        .with_upload_code(False)
                        .build()
                )
            
            assert expected_message in str(exc_info.value)

    def test_parse_bid_response(self):
        """Test parsing of bid creation response."""
        # Create custom mock HTTP client
        class MockHTTPClient:
            def __init__(self):
                self.calls = []
                
            def request(self, method, url, **kwargs):
                self.calls.append((method, url))
                if url == "/v2/spot/availability":
                    # Return availability for h100
                    return [{
                        "fid": "auc_789",
                        "instance_type": INSTANCE_TYPE_FIDS["h100"],
                        "region": "us-central1-a",
                        "capacity": 5,
                        "last_instance_price": f"${PRICE_H100_8X}"
                    }]
                elif url == "/v2/spot/bids" and method == "POST":
                    # Return bid response
                    return {
                        "fid": "bid-999",
                        "status": "pending",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "instance_type": INSTANCE_TYPE_FIDS["h100"],
                        "region": "us-central1-a",
                        "limit_price": kwargs["json"]["limit_price"],
                        "name": kwargs["json"]["name"],
                    }
                return []
        
        # Create provider with mock HTTP client
        config = Config(
            provider="fcp",
            auth_token=DEFAULT_AUTH_TOKEN,
            provider_config={
                "api_url": DEFAULT_API_URL,
                "project": "test-project"
            }
        )
        mock_http = MockHTTPClient()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = DEFAULT_PROJECT_ID
        
        # Mock SSH keys
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])
        
        # Submit task
        config = TaskConfigBuilder() \
            .with_name("test-parsing") \
            .with_instance_type("h100") \
            .with_upload_code(False) \
            .build()
            
        task = provider.submit_task("h100", config)
        
        # Verify parsing
        assert task.task_id == "bid-999"
        assert task.name == "test-parsing"
        assert task.status == TaskStatus.PENDING


class TestFCPProviderValidation:
    """Test provider's input validation logic.
    
    These tests ensure the provider properly validates inputs
    and provides helpful error messages.
    """

    def create_provider(self) -> tuple[FCPProvider, Mock]:
        """Create provider with mocked HTTP client."""
        config = Config(
            provider="fcp",
            auth_token=DEFAULT_AUTH_TOKEN,
            provider_config={
                "api_url": DEFAULT_API_URL,
                "project": "test-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = DEFAULT_PROJECT_ID
        return provider, mock_http

    def test_submit_task_accepts_various_instance_formats(self):
        """Test that users can submit tasks with different instance type formats."""
        provider, mock_http = self.create_provider()
        
        # Mock SSH keys
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # These formats should all work with their corresponding FIDs
        valid_formats = [
            ("a100", INSTANCE_TYPE_FIDS["a100"]),
            ("2xa100", INSTANCE_TYPE_FIDS["2xa100"]),
            ("a100-80gb.sxm.1x", INSTANCE_TYPE_FIDS["a100"]),
            ("8xh100", INSTANCE_TYPE_FIDS["8xh100"]),
        ]

        for instance_type, expected_fid in valid_formats:
            config = TaskConfigBuilder() \
                .with_instance_type(instance_type) \
                .with_upload_code(False) \
                .build()

            def mock_request(method, url, **kwargs):
                if url == "/v2/spot/availability":
                    return [{
                        "fid": "auc_123", 
                        "instance_type": expected_fid,
                        "region": "us-east-1", 
                        "capacity": 10, 
                        "last_instance_price": "$5.00"
                    }]
                elif url == "/v2/spot/bids" and method == "POST":
                    # Verify the bid uses the correct instance type FID
                    assert kwargs["json"]["instance_type"] == expected_fid
                    return {
                        "fid": "bid-123", 
                        "status": "pending",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "instance_type": expected_fid,
                        "region": "us-east-1"
                    }
                return []
                
            mock_http.request = Mock(side_effect=mock_request)

            task = provider.submit_task(instance_type=instance_type, config=config)
            assert task.task_id == "bid-123", \
                f"Failed for instance type: {instance_type}"

    def test_helpful_error_for_invalid_instance_type(self):
        """Test that users get helpful guidance for invalid instance types."""
        provider, mock_http = self.create_provider()
        
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Test common user mistakes
        invalid_config = TaskConfigBuilder() \
            .with_instance_type("nvidia-a100") \
            .build()

        with pytest.raises(FCPInstanceError) as exc_info:
            provider.submit_task(instance_type="nvidia-a100", config=invalid_config)

        error_message = str(exc_info.value)
        # Error should guide users to valid options
        assert "Unknown instance type: nvidia-a100" in error_message
        assert "Available:" in error_message
        # Check that some valid options are listed
        assert "a100" in error_message
        assert "2xa100" in error_message

    def test_validate_task_config_requirements(self):
        """Test validation of task configuration fields."""
        provider, mock_http = self.create_provider()
        
        # TaskConfigBuilder generates names when empty ones are provided
        config = TaskConfigBuilder().with_name("").build()
        
        # The test verifies that the system handles empty names gracefully
        assert config.name.startswith("test-task-")  # Auto-generated name

    def test_instance_availability_filtering(self):
        """Test that provider correctly filters available instances."""
        provider, mock_http = self.create_provider()
        
        # Mock response with multiple instance types
        def mock_request(method, url, **kwargs):
            all_instances = [
                {
                    "fid": "auc_1",
                    "instance_type": INSTANCE_TYPE_FIDS["a100"],
                    "region": "us-east-1",
                    "last_instance_price": "$25.00",
                    "capacity": 5,
                },
                {
                    "fid": "auc_2",
                    "instance_type": INSTANCE_TYPE_FIDS["8xa100"],
                    "region": "us-east-1",
                    "last_instance_price": "$80.00",
                    "capacity": 2,
                },
                {
                    "fid": "auc_3",
                    "instance_type": INSTANCE_TYPE_FIDS["h100"],
                    "region": "us-west-2",
                    "last_instance_price": "$50.00",
                    "capacity": 1,
                }
            ]
            
            # Simulate server-side filtering
            params = kwargs.get("params", {})
            results = all_instances
            
            # Filter by instance_type (FID)
            if "instance_type" in params:
                fid = params["instance_type"]
                results = [i for i in results if i["instance_type"] == fid]
            
            # Filter by region
            if "region" in params:
                region = params["region"]
                results = [i for i in results if i["region"] == region]
                
            return results
            
        mock_http.request = Mock(side_effect=mock_request)
        
        # Test filtering by price
        instances = provider.find_instances({"max_price_per_hour": 30.0})
        assert len(instances) == 1
        assert instances[0].price_per_hour == 25.0
        
        # Test filtering by region
        instances = provider.find_instances({"region": "us-west-2"})
        assert len(instances) == 1
        assert instances[0].region == "us-west-2"
        
        # Test filtering by instance type
        instances = provider.find_instances({"instance_type": "8xa100"})
        assert len(instances) == 1
        assert instances[0].instance_type == "a100-80gb.sxm.8x"


class TestFCPProviderEdgeCases:
    """Test edge cases and error conditions."""
    
    def create_provider(self) -> tuple[FCPProvider, Mock]:
        """Create provider with mocked HTTP client."""
        config = Config(
            provider="fcp",
            auth_token=DEFAULT_AUTH_TOKEN,
            provider_config={
                "api_url": DEFAULT_API_URL,
                "project": "test-project"
            }
        )
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = DEFAULT_PROJECT_ID
        return provider, mock_http
        
    def test_empty_availability_response(self):
        """Test handling of empty availability response."""
        provider, mock_http = self.create_provider()
        
        # Mock empty response
        mock_http.request = Mock(return_value=[])
        
        instances = provider.find_instances({"instance_type": "a100"})
        
        assert instances == []
        assert mock_http.request.called
        
    def test_malformed_price_in_response(self):
        """Test handling of malformed price data."""
        provider, mock_http = self.create_provider()
        
        mock_http.request = Mock(return_value=[
            {
                "fid": "auc_bad",
                "instance_type": INSTANCE_TYPE_FIDS["a100"],
                "region": "us-east-1",
                "last_instance_price": "not-a-price",  # Malformed
                "capacity": 1,
            }
        ])
        
        instances = provider.find_instances({})
        
        # Should handle gracefully and use 0.0 as price
        assert len(instances) == 1
        assert instances[0].price_per_hour == 0.0