"""Unit tests for FCP provider implementation - Updated with TestConstants.

This is an example of updating the test suite to use centralized constants
instead of magic strings and numbers. This follows the principle of no
magic values in tests.
"""

from datetime import datetime, timedelta
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
from tests.testing.constants import TestConstants
from tests.testing.factories import FCPModelFactory, TaskFactory


class TestFCPAdapterUpdated:
    """Test our adapter logic for converting between FCP and domain models."""

    def test_bid_status_mapping(self):
        """Test that we correctly map FCP statuses to our domain statuses."""
        # Use constants for test data
        test_cases = [
            (status, TaskStatus[expected])
            for status, expected in TestConstants.FCP_STATUS_MAPPINGS.items()
        ]

        for fcp_status, expected_status in test_cases:
            bid = FCPBid(
                fid=TestConstants.get_mock_bid_id(),
                name=TestConstants.get_test_task_name(),
                status=fcp_status,
                limit_price=str(TestConstants.TEST_PRICE_MEDIUM),
                created_at=datetime.now(),
                project=TestConstants.MOCK_PROJECT_ID,
                created_by=TestConstants.MOCK_USER_ID,
                instance_quantity=TestConstants.DEFAULT_NUM_INSTANCES,
                instance_type=TestConstants.TEST_INSTANCE_TYPE_ID,
                region=TestConstants.DEFAULT_REGION,
            )

            task = FCPAdapter.bid_to_task(bid)

            assert task.status == expected_status, f"Failed to map {fcp_status}"

    def test_bid_to_task_with_instances(self):
        """Test bid to task conversion with instance details."""
        # Create test data using factories
        created_at = datetime.now()
        started_at = created_at + timedelta(minutes=TestConstants.TEST_STARTUP_DELAY_MINUTES)

        bid = FCPModelFactory.create_fcp_bid(
            status="allocated",
            name=TestConstants.get_test_task_name("gpu-training")
        )
        bid.limit_price = str(TestConstants.TEST_PRICE_HIGH)
        bid.created_at = created_at

        instances = [
            FCPModelFactory.create_fcp_instance(
                bid_id=bid.fid,
                status="running"
            )
        ]
        instances[0].created_at = started_at

        # Convert
        task = FCPAdapter.bid_to_task(
            bid, 
            instances, 
            instance_type_name=TestConstants.TEST_INSTANCE_TYPE_NAME
        )

        # Verify conversion
        assert task.task_id == bid.fid
        assert task.name == bid.name
        assert task.status == TaskStatus.RUNNING
        assert task.instance_type == TestConstants.TEST_INSTANCE_TYPE_NAME

    def test_price_parsing(self):
        """Test price parsing handles various formats."""
        test_cases = [
            (str(TestConstants.TEST_PRICE_MEDIUM), TestConstants.TEST_PRICE_MEDIUM),
            (TestConstants.TEST_PRICE_STRING_MEDIUM, TestConstants.TEST_PRICE_MEDIUM),
            (str(TestConstants.TEST_PRICE_VERY_HIGH), TestConstants.TEST_PRICE_VERY_HIGH),
            (TestConstants.TEST_PRICE_STRING_LOW.replace("$", ""), TestConstants.TEST_PRICE_LOW),
            # Invalid cases
            ("invalid", TestConstants.TEST_PRICE_INVALID),
            ("", TestConstants.TEST_PRICE_INVALID),
        ]

        for input_price, expected in test_cases:
            result = FCPAdapter._parse_price(input_price)
            assert abs(result - expected) < TestConstants.PRICE_TOLERANCE, \
                f"Failed to parse {input_price}"

    def test_runtime_calculation(self):
        """Test runtime calculation logic."""
        start = datetime.now()
        test_cases = [
            (start + timedelta(hours=1), 1.0),
            (start + timedelta(hours=2.5), 2.5),
            (start + timedelta(minutes=30), 0.5),
        ]

        for end, expected_hours in test_cases:
            hours = FCPAdapter._calculate_runtime_hours(start, end)
            assert abs(hours - expected_hours) < TestConstants.RUNTIME_PRECISION, \
                f"Wrong hours for {end}"


class TestFCPProviderParsing:
    """Test provider's response parsing logic."""

    @pytest.fixture
    def provider(self):
        """Create provider with mocked HTTP client."""
        config = Config(provider="fcp")
        http_client = Mock()
        instance_resolver = Mock()
        project_resolver = Mock(
            resolve_project=Mock(return_value=TestConstants.MOCK_PROJECT_ID)
        )
        
        return FCPProvider(
            config=config,
            http_client=http_client,
            instance_type_resolver=instance_resolver,
            project_resolver=project_resolver,
        )

    def test_empty_response_handling(self, provider):
        """Test handling of empty API responses."""
        provider.http.request = Mock(return_value={"bids": []})
        
        tasks = provider.list_tasks()
        
        assert tasks == []
        assert provider.http.request.called

    def test_malformed_bid_handling(self, provider):
        """Test handling of malformed bid data."""
        # Create malformed response with factory, then break it
        bid_data = FCPModelFactory.create_fcp_bid().__dict__
        del bid_data['status']  # Remove required field
        
        provider.http.request = Mock(return_value={"bids": [bid_data]})
        
        # Should handle gracefully
        tasks = provider.list_tasks()
        
        # Verify we handle malformed data without crashing
        assert isinstance(tasks, list)

    def test_large_task_list_handling(self, provider):
        """Test handling of large task lists."""
        # Generate large response using factory
        large_bid_list = [
            FCPModelFactory.create_fcp_bid(
                name=f"{TestConstants.TEST_TASK_PREFIX}{i:04d}"
            ).__dict__
            for i in range(TestConstants.MAX_INSTANCES_PER_TASK * 10)
        ]
        
        provider.http.request = Mock(return_value={"bids": large_bid_list})
        
        tasks = provider.list_tasks()
        
        assert len(tasks) == len(large_bid_list)
        # Verify all tasks were parsed
        for i, task in enumerate(tasks):
            assert f"{TestConstants.TEST_TASK_PREFIX}{i:04d}" in task.name