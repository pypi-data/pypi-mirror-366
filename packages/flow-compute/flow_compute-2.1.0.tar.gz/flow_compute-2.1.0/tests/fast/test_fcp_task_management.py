"""Unit tests for FCP provider task management.

These tests focus on task submission, status checking, cancellation,
and lifecycle management.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskStatus
from flow.providers.fcp.adapters.models import FCPAdapter
from flow.providers.fcp.core.errors import FCPInstanceError
from flow.providers.fcp.core.models import FCPBid
from flow.providers.fcp.provider import FCPProvider
from tests.support.framework import TaskConfigBuilder


@pytest.mark.unit
@pytest.mark.medium


class TestFCPTaskSubmission:
    """Test task submission functionality."""

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

    def test_submit_task_successful(self, provider):
        """Test successful task submission."""
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Mock API responses
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
                    "name": "test-task",
                    "status": "pending",
                    "limit_price": "5.00",
                    "created_at": datetime.now().isoformat(),
                    "project": "proj-123",
                    "created_by": "user-123",
                    "instance_quantity": 1,
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-east-1"
                }
            return []

        provider.http.request = Mock(side_effect=mock_request)

        # Submit task
        task = provider.submit_task(
            instance_type="a100",
            config=TaskConfigBuilder().with_instance_type("a100").with_upload_code(False).build()
        )

        assert task.task_id == "bid-123"
        assert task.name == "test-task"
        assert task.status == TaskStatus.PENDING

    @pytest.mark.timeout(5)  # This test should complete within 5 seconds
    def test_submit_task_with_multiple_regions(self, provider):
        """Test task submission tries multiple regions."""
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        availability_call_count = 0

        def mock_request(method, url, **kwargs):
            nonlocal availability_call_count
            if url == "/v2/spot/availability":
                availability_call_count += 1
                if availability_call_count == 1:
                    # First region has no availability
                    return []
                else:
                    # Second region has availability
                    return [{
                        "fid": "auc_456",
                        "instance_type": "it_MsIRhxj3ccyVWGfP",
                        "region": "us-west-2",
                        "capacity": 5,
                        "last_instance_price": "$6.00"
                    }]
            elif url == "/v2/spot/bids" and method == "POST":
                # Verify we're bidding in the second region
                assert kwargs["json"]["region"] == "us-west-2"
                return {
                    "fid": "bid-456",
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                    "instance_type": "it_MsIRhxj3ccyVWGfP",
                    "region": "us-west-2"
                }
            return []

        provider.http.request = Mock(side_effect=mock_request)

        # Submit task with multiple regions
        config = TaskConfigBuilder()\
            .with_instance_type("a100")\
            .with_regions(["us-east-1", "us-west-2"])\
            .with_upload_code(False)\
            .build()

        task = provider.submit_task(instance_type="a100", config=config)

        assert task.task_id == "bid-456"
        # Should have tried both regions
        assert availability_call_count == 2

    def test_submit_task_no_availability(self, provider):
        """Test task submission when no instances available."""
        # Mock SSH key manager
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # Mock no availability in any region
        provider.http.request = Mock(return_value=[])

        config = TaskConfigBuilder()\
            .with_instance_type("a100")\
            .with_regions(["us-east-1", "us-west-2"])\
            .with_upload_code(False)\
            .build()

        with pytest.raises(FCPInstanceError) as exc_info:
            provider.submit_task(instance_type="a100", config=config)

        assert "No a100 instances available" in str(exc_info.value)

    def test_submit_task_accepts_various_instance_formats(self, provider):
        """Test that users can submit tasks with different instance type formats."""
        # Mock SSH keys
        provider.ssh_key_manager.ensure_keys = Mock(return_value=["key-123"])

        # These formats should all work with their corresponding FIDs
        valid_formats = [
            ("a100", "it_MsIRhxj3ccyVWGfP"),           # Simple name -> 1xa100
            ("2xa100", "it_5M6aGxGovNeX5ltT"),         # Count prefix
            ("a100-80gb.sxm.1x", "it_MsIRhxj3ccyVWGfP"), # FCP format
            ("8xh100", "it_5ECSoHQjLBzrp5YM"),         # H100 variant
        ]

        for instance_type, expected_fid in valid_formats:
            config = TaskConfigBuilder().with_instance_type(instance_type).with_upload_code(False).build()

            def mock_request(method, url, **kwargs):
                if url == "/v2/spot/availability":
                    # Return availability for the expected FID
                    return [{"fid": "auc_123", "instance_type": expected_fid,
                            "region": "us-east-1", "capacity": 10, "last_instance_price": "$5.00"}]
                elif url == "/v2/spot/bids" and method == "POST":
                    # Verify the bid uses the correct instance type FID
                    assert kwargs["json"]["instance_type"] == expected_fid
                    return {"fid": "bid-123", "status": "pending",
                           "created_at": datetime.now().isoformat(),
                           "instance_type": expected_fid,
                           "region": "us-east-1"}
                return []
            provider.http.request = Mock(side_effect=mock_request)

            task = provider.submit_task(instance_type=instance_type, config=config)
            assert task.task_id == "bid-123", f"Failed for instance type: {instance_type}"


class TestFCPTaskLifecycle:
    """Test task status and lifecycle management."""

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
        provider._project_id = "proj-123"
        return provider

    def test_get_task_status(self, provider):
        """Test retrieving task status."""
        # Mock bid and instance data
        bid_data = {
            "fid": "bid-123",
            "name": "test-task",
            "status": "allocated",
            "limit_price": "25.60",
            "created_at": datetime.now().isoformat(),
            "project": "proj-123",
            "created_by": "user-123",
            "instance_quantity": 1,
            "instance_type": "it_MsIRhxj3ccyVWGfP",
            "region": "us-east-1",
        }

        instance_data = [{
            "fid": "i-123",
            "bid_id": "bid-123",
            "status": "running",
            "created_at": datetime.now().isoformat(),
            "instance_type": "it_MsIRhxj3ccyVWGfP",
            "region": "us-east-1",
        }]

        def mock_request(method, url, **kwargs):
            if url == "/v2/spot/bids/bid-123":
                return bid_data
            elif url == "/v2/spot/instances" and kwargs.get("params", {}).get("bid_id") == "bid-123":
                return instance_data
            return None

        provider.http.request = Mock(side_effect=mock_request)

        task = provider.get_task_status("bid-123")

        assert task.task_id == "bid-123"
        assert task.status == TaskStatus.RUNNING
        assert task.name == "test-task"

    def test_cancel_task(self, provider):
        """Test task cancellation."""
        # Mock successful cancellation
        provider.http.request = Mock(return_value={
            "fid": "bid-123",
            "status": "terminating"
        })

        provider.cancel_task("bid-123")

        # Verify API call
        provider.http.request.assert_called_once_with(
            "DELETE",
            "/v2/spot/bids/bid-123"
        )

    def test_list_tasks(self, provider):
        """Test listing all tasks."""
        # Mock multiple bids
        bids_data = [
            {
                "fid": "bid-123",
                "name": "task-1",
                "status": "running",
                "limit_price": "10.00",
                "created_at": datetime.now().isoformat(),
                "project": "proj-123",
                "created_by": "user-123",
                "instance_quantity": 1,
                "instance_type": "it_MsIRhxj3ccyVWGfP",
                "region": "us-east-1",
            },
            {
                "fid": "bid-456",
                "name": "task-2",
                "status": "completed",
                "limit_price": "15.00",
                "created_at": datetime.now().isoformat(),
                "project": "proj-123",
                "created_by": "user-123",
                "instance_quantity": 1,
                "instance_type": "it_5M6aGxGovNeX5ltT",
                "region": "us-west-2",
            }
        ]

        provider.http.request = Mock(return_value=bids_data)

        tasks = provider.list_tasks()

        assert len(tasks) == 2
        assert tasks[0].task_id == "bid-123"
        assert tasks[0].status == TaskStatus.RUNNING
        assert tasks[1].task_id == "bid-456"
        assert tasks[1].status == TaskStatus.COMPLETED


class TestFCPTaskStatusMapping:
    """Test task status mapping logic."""

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
                created_at=datetime.now(),
                # Add required fields
                project="proj-123",
                created_by="user-123",
                instance_quantity=1,
                instance_type="it_XqgKWbhZ5gznAYsG",
                region="us-east-1",
            )

            task = FCPAdapter.bid_to_task(bid)

            assert task.status == expected_status, f"Failed to map {fcp_status}"