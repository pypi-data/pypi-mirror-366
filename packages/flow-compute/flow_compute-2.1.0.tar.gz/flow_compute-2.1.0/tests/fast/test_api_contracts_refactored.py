"""Refactored API contract tests using fixture files.

This demonstrates how to use the new fixture system instead of
hardcoded API responses.
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from flow.providers.fcp.api.types import (
    AuctionModel,
    BidModel,
    InstanceTypeModel,
    ProjectModel,
    VolumeModel,
)
from tests.support.fixtures.api_responses import fcp_responses


class TestAPIResponseContractsRefactored:
    """Test API response models using fixture data."""

    def test_project_response_contract(self):
        """Test ProjectModel parses API response correctly."""
        # Use fixture instead of hardcoded response
        api_response = fcp_responses.project_success
        
        project = ProjectModel(**api_response)
        assert project.fid == "proj-abc123"
        assert project.name == "my-project"
        assert project.created_at == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    def test_instance_type_response_contract(self):
        """Test InstanceTypeModel handles various GPU configurations."""
        # Use fixtures for different instance types
        test_cases = [
            fcp_responses.instance_type_gpu_single,
            fcp_responses.instance_type_gpu_multi,
            fcp_responses.instance_type_cpu_only,
        ]
        
        for case in test_cases:
            instance = InstanceTypeModel(**case)
            assert instance.name == case["name"]
            assert instance.fid == case["fid"]
            assert instance.cpu_cores == case["num_cpus"]
            assert instance.ram_gb == case["ram"]
            
            if case["gpus"]:
                assert len(instance.gpus) == len(case["gpus"])
                for i, gpu in enumerate(instance.gpus):
                    assert gpu.name == case["gpus"][i]["name"]
                    assert gpu.vram_gb == case["gpus"][i]["vram_gb"]
                    assert gpu.count == case["gpus"][i]["count"]
            else:
                assert instance.gpus is None or instance.gpus == []

    def test_auction_response_contract(self):
        """Test AuctionModel parses API response correctly."""
        api_response = fcp_responses.auction_available
        
        auction = AuctionModel(**api_response)
        assert auction.fid == "auction-123"
        assert auction.instance_type == "gpu.nvidia.a100"
        assert auction.region == "us-central1"
        assert auction.last_instance_price == "$2.50"
        assert auction.capacity == 10

    def test_bid_state_responses(self):
        """Test BidModel handles different bid states."""
        # Use fixtures for different bid states
        bid_states = {
            "pending": fcp_responses.bid_pending,
            "won": fcp_responses.bid_won,
            "lost": fcp_responses.bid_lost,
            "expired": fcp_responses.bid_expired,
        }
        
        for state, api_response in bid_states.items():
            bid = BidModel(**api_response)
            assert bid.fid == f"bid-{state}"
            assert bid.status == state
            assert bid.project == "proj-123"
            
            if state == "won":
                assert bid.allocation_id == "alloc-789"
            else:
                assert not hasattr(bid, 'allocation_id') or bid.allocation_id is None

    def test_volume_response_contracts(self):
        """Test VolumeModel with different volume types."""
        # Test standard block volume
        block_response = fcp_responses.volume_available
        block_vol = VolumeModel(**block_response)
        assert block_vol.fid == "vol-123"
        assert block_vol.interface == "block"
        assert block_vol.size_gb == 100
        
        # Test file share volume
        share_response = fcp_responses.volume_file_share
        share_vol = VolumeModel(**share_response)
        assert share_vol.fid == "vol-456"
        assert share_vol.interface == "file"
        assert share_vol.mount_targets[0]["ip"] == "10.0.0.1"
        
        # Test attached volume
        attached_response = fcp_responses.volume_attached
        attached_vol = VolumeModel(**attached_response)
        assert attached_vol.status == "attached"
        assert "instance-123" in attached_vol.attached_to

    def test_custom_responses(self):
        """Test creating custom responses from fixtures."""
        # Create custom task with specific fields
        custom_task = fcp_responses.custom_task(
            task_id="custom-123",
            name="my-custom-task",
            status="pending"
        )
        assert custom_task["task_id"] == "custom-123"
        assert custom_task["name"] == "my-custom-task"
        assert custom_task["status"] == "pending"
        
        # Create custom volume
        custom_volume = fcp_responses.custom_volume(
            fid="vol-custom",
            size_gb=2000,
            region="eu-west1"
        )
        assert custom_volume["fid"] == "vol-custom"
        assert custom_volume["size_gb"] == 2000
        assert custom_volume["region"] == "eu-west1"

    def test_error_responses(self):
        """Test error response handling."""
        # Validation error
        validation_error = fcp_responses.error_validation
        assert len(validation_error["detail"]) == 3
        assert validation_error["detail"][0]["type"] == "missing"
        
        # Not found error
        not_found = fcp_responses.error_not_found
        assert not_found["code"] == "NOT_FOUND"
        
        # Rate limit error
        rate_limit = fcp_responses.error_rate_limit
        assert rate_limit["retry_after"] == 60
        
        # Custom error
        custom_error = fcp_responses.custom_error(
            code="CUSTOM_ERROR",
            message="Something went wrong",
            details={"field": "value"}
        )
        assert custom_error["code"] == "CUSTOM_ERROR"
        assert custom_error["details"]["field"] == "value"


class TestMockingWithFixtures:
    """Demonstrate using fixtures in mock scenarios."""
    
    def test_mock_api_client_with_fixtures(self):
        """Show how to use fixtures with mocks."""
        from unittest.mock import Mock, patch
        
        # Mock API client using fixtures
        mock_client = Mock()
        
        # Use fixtures for return values
        mock_client.get_project.return_value = fcp_responses.project_success
        mock_client.list_tasks.return_value = fcp_responses.large_task_list
        mock_client.get_task.return_value = fcp_responses.task_running
        mock_client.create_volume.return_value = fcp_responses.volume_available
        
        # Test code can now use consistent, maintainable responses
        project = mock_client.get_project("proj-123")
        assert project["name"] == "my-project"
        
        tasks = mock_client.list_tasks()
        assert len(tasks["tasks"]) == 3
        assert tasks["next_token"] == "token-123"

    @patch('flow.providers.fcp.api.client.FCPAPIClient')
    def test_provider_with_fixture_responses(self, mock_client_class):
        """Test provider using fixture responses."""
        from flow.providers.fcp.provider import FCPProvider
        
        # Configure mock instance
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        # Use fixtures for all responses
        mock_instance.find_instances.return_value = fcp_responses.allocations_list
        mock_instance.create_bid.return_value = fcp_responses.bid_pending
        mock_instance.get_bid.side_effect = [
            fcp_responses.bid_pending,
            fcp_responses.bid_won,
        ]
        mock_instance.create_task.return_value = fcp_responses.task_created
        
        # Now provider tests use consistent fixture data
        provider = FCPProvider()
        
        # Simulate task submission
        from flow.api.models import TaskConfig
        config = TaskConfig(
            name="test-task",
            instance_type="gpu.nvidia.a100",
            command=["python", "train.py"]
        )
        
        # Provider would use the mocked responses
        # This ensures tests are maintainable and consistent