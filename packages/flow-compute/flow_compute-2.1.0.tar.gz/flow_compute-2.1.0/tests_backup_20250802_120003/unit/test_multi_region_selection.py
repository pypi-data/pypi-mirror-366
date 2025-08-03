"""Unit tests for multi-region instance selection functionality."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig
from flow.errors import ResourceNotFoundError
from flow.providers.fcp.core.models import FCPAuction
from flow.providers.fcp.provider import FCPProvider


class TestMultiRegionSelection:
    """Test the multi-region availability and selection logic."""

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
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])
        return provider

    def test_check_availability_multiple_regions(self, provider):
        """Test checking availability across multiple regions."""
        # Mock the availability API response
        mock_availability = [
            {
                "fid": "auc_1",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "region": "us-east-1",
                "capacity": 5,
                "last_instance_price": "$5.00"
            },
            {
                "fid": "auc_2",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "region": "us-west-2",
                "capacity": 10,
                "last_instance_price": "$4.50"
            },
            {
                "fid": "auc_3",
                "instance_type": "it_5M6aGxGovNeX5ltT",  # 2xa100
                "region": "us-east-1",
                "capacity": 2,
                "last_instance_price": "$10.00"
            }
        ]

        provider.http.request = Mock(return_value=mock_availability)

        # Check availability for a100
        availability = provider._check_availability("a100")

        # Should have found a100 in two regions
        assert len(availability) == 2
        assert "us-east-1" in availability
        assert "us-west-2" in availability

        # Should have selected the cheapest option per region
        assert provider._parse_price(availability["us-east-1"].last_instance_price) == 5.0
        assert provider._parse_price(availability["us-west-2"].last_instance_price) == 4.5

        # Should have correct capacity
        assert availability["us-east-1"].capacity == 5
        assert availability["us-west-2"].capacity == 10

    def test_select_best_region_by_capacity(self, provider):
        """Test selecting region with highest capacity."""
        availability = {
            "us-east-1": FCPAuction(
                fid="auc_1",
                instance_type="it_MsIRhxj3ccyVWGfP",
                region="us-east-1",
                capacity=5,
                last_instance_price="$5.00"
            ),
            "us-west-2": FCPAuction(
                fid="auc_2",
                instance_type="it_MsIRhxj3ccyVWGfP",
                region="us-west-2",
                capacity=10,
                last_instance_price="$5.00"
            )
        }

        # With same price, should select higher capacity
        best_region = provider._select_best_region(availability)
        assert best_region == "us-west-2"

    def test_select_best_region_by_price(self, provider):
        """Test selecting region with lowest price."""
        availability = {
            "us-east-1": FCPAuction(
                fid="auc_1",
                instance_type="it_MsIRhxj3ccyVWGfP",
                region="us-east-1",
                capacity=10,
                last_instance_price="$5.00"
            ),
            "us-west-2": FCPAuction(
                fid="auc_2",
                instance_type="it_MsIRhxj3ccyVWGfP",
                region="us-west-2",
                capacity=10,
                last_instance_price="$4.50"
            )
        }

        # With same capacity, should select lower price
        best_region = provider._select_best_region(availability)
        assert best_region == "us-west-2"

    def test_select_preferred_region(self, provider):
        """Test respecting user's preferred region."""
        availability = {
            "us-east-1": FCPAuction(
                fid="auc_1",
                instance_type="it_MsIRhxj3ccyVWGfP",
                region="us-east-1",
                capacity=10,
                last_instance_price="$5.00"
            ),
            "us-west-2": FCPAuction(
                fid="auc_2",
                instance_type="it_MsIRhxj3ccyVWGfP",
                region="us-west-2",
                capacity=5,
                last_instance_price="$10.00"  # More expensive
            )
        }

        # Should respect preference even if more expensive
        best_region = provider._select_best_region(availability, preferred_region="us-west-2")
        assert best_region == "us-west-2"

    def test_no_availability_error(self, provider):
        """Test error when no instances available anywhere."""
        # Mock empty availability response
        provider.http.request = Mock(return_value=[])

        config = TaskConfig(
            name="test-task",
            instance_type="a100",
            command=["echo", "test"],
            upload_code=False
        )

        # Should raise ResourceNotFoundError
        with pytest.raises(ResourceNotFoundError) as exc_info:
            provider.submit_task("a100", config)

        assert "No a100 instances available" in str(exc_info.value)
        assert "all regions" in str(exc_info.value)

    def test_submit_task_with_auto_region(self, provider):
        """Test task submission with automatic region selection."""
        # Mock availability response
        mock_availability = [
            {
                "fid": "auc_best",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "region": "us-west-2",
                "capacity": 20,
                "last_instance_price": "$3.00"
            },
            {
                "fid": "auc_worse",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "region": "us-east-1",
                "capacity": 5,
                "last_instance_price": "$5.00"
            }
        ]

        # Mock the bid submission response
        mock_bid_response = {
            "fid": "bid-123",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "instance_type": "it_MsIRhxj3ccyVWGfP",
            "region": "us-west-2"
        }

        def mock_request(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return mock_availability
            elif url == "/v2/spot/bids" and method == "POST":
                # Verify the request selected the best region
                assert kwargs["json"]["region"] == "us-west-2"
                assert kwargs["json"]["auction_id"] == "auc_best"
                return mock_bid_response
            return []

        provider.http.request = Mock(side_effect=mock_request)

        config = TaskConfig(
            name="test-task",
            instance_type="a100",
            command=["echo", "test"],
            upload_code=False
        )

        # Submit without specifying region
        task = provider.submit_task("a100", config)

        assert task.task_id == "bid-123"
        assert task.region == "us-west-2"  # Auto-selected best region

    def test_submit_task_with_specified_region(self, provider):
        """Test task submission with user-specified region."""
        # Mock availability response
        mock_availability = [
            {
                "fid": "auc_preferred",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "region": "eu-west-1",
                "capacity": 3,
                "last_instance_price": "$8.00"
            },
            {
                "fid": "auc_better",
                "instance_type": "it_MsIRhxj3ccyVWGfP",  # a100
                "region": "us-west-2",
                "capacity": 20,
                "last_instance_price": "$3.00"
            }
        ]

        # Mock the bid submission response
        mock_bid_response = {
            "fid": "bid-456",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "instance_type": "it_MsIRhxj3ccyVWGfP",
            "region": "eu-west-1"
        }

        def mock_request(method, url, **kwargs):
            if url == "/v2/spot/availability":
                return mock_availability
            elif url == "/v2/spot/bids" and method == "POST":
                # Verify the request used the preferred region
                assert kwargs["json"]["region"] == "eu-west-1"
                assert kwargs["json"]["auction_id"] == "auc_preferred"
                return mock_bid_response
            return []

        provider.http.request = Mock(side_effect=mock_request)

        config = TaskConfig(
            name="test-task",
            instance_type="a100",
            command=["echo", "test"],
            region="eu-west-1",  # User preference
            upload_code=False
        )

        # Submit with specified region
        task = provider.submit_task("a100", config)

        assert task.task_id == "bid-456"
        assert task.region == "eu-west-1"  # Used preferred region
