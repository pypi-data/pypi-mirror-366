"""Integration tests for FCP user journeys with instance resolution.

These tests verify the complete flow from user-friendly instance names
to successful API calls and task creation.

IMPROVEMENTS:
- Mock only at HTTP boundary (external dependency)
- Each test completely isolated
- No shared provider fixture creating dependencies
- Clear test data builders
- Explicit test scenarios
"""

from typing import Any, Dict, List, Optional
from unittest.mock import Mock

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig
from flow.providers.fcp.core.errors import FCPInstanceError
from flow.providers.fcp.provider import FCPProvider

# Test constants
DEFAULT_PROJECT_ID = "proj-123"
DEFAULT_SSH_KEY_ID = "ssh-key-123"
DEFAULT_REGION = "us-central1-a"

# Instance type mappings for tests
A100_FID = "it_MsIRhxj3ccyVWGfP"  # a100
A100_8X_FID = "it_J7OyNf9idfImLIFo"  # 8xa100
H100_FID = "it_5ECSoHQjLBzrp5YM"  # h100


class MockHTTPClient:
    """Mock HTTP client that simulates FCP API responses.
    
    This is the ONLY mock in these tests - we mock at the external boundary.
    Everything else runs real code.
    """
    
    def __init__(self):
        self.request_history: List[Dict[str, Any]] = []
        self.base_url = "https://api.mlfoundry.com"  # Add base_url attribute
        
    def request(self, method: str, url: str, **kwargs) -> Any:
        """Mock HTTP request handler."""
        # Record request for assertions
        self.request_history.append({
            "method": method,
            "url": url,
            "kwargs": kwargs
        })
        
        # Route to appropriate handler
        if url == "/v2/projects":
            return self._handle_projects()
        elif url == "/v2/ssh-keys":
            return self._handle_ssh_keys()
        elif url == "/v2/spot/bids" and method == "POST":
            return self._handle_create_bid(kwargs.get("json", {}))
        elif url == "/v2/spot/availability":
            return self._handle_availability(kwargs.get("params", {}))
        return []
        
    def _handle_projects(self) -> List[Dict[str, Any]]:
        """Mock project list response."""
        return [{
            "fid": DEFAULT_PROJECT_ID,
            "name": "test-project",
            "created_at": "2024-01-01T00:00:00Z"
        }]
        
    def _handle_ssh_keys(self) -> List[Dict[str, Any]]:
        """Mock SSH key list response."""
        return [{
            "fid": DEFAULT_SSH_KEY_ID,
            "name": "test-key",
            "public_key": "ssh-rsa AAAAB3... test@example.com"
        }]
        
    def _handle_create_bid(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock bid creation response."""
        return {
            "fid": f"bid_{len(self.request_history)}",
            "status": "pending",
            "instance_type": payload.get("instance_type"),
            "region": payload.get("region", DEFAULT_REGION)
        }
        
    def _handle_availability(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Mock availability response based on query params."""
        instance_type_fid = params.get("instance_type")
        
        # Map FIDs to mock availability
        availability_map = {
            A100_FID: {
                "fid": "auc_a100_123",
                "instance_type": A100_FID,
                "last_instance_price": "$25.00",
                "region": DEFAULT_REGION,
                "capacity": 5,
            },
            A100_8X_FID: {
                "fid": "auc_8xa100_123",
                "instance_type": A100_8X_FID,
                "last_instance_price": "$80.00",
                "region": DEFAULT_REGION,
                "capacity": 2,
            },
            H100_FID: {
                "fid": "auc_h100_123",
                "instance_type": H100_FID,
                "last_instance_price": "$50.00",
                "region": DEFAULT_REGION,
                "capacity": 2,
            }
        }
        
        if instance_type_fid in availability_map:
            return [availability_map[instance_type_fid]]
        
        # Return general availability if no specific type requested
        if not instance_type_fid:
            return list(availability_map.values())
            
        return []
        
    def get_bid_creation_requests(self) -> List[Dict[str, Any]]:
        """Get all bid creation requests for assertions."""
        return [
            req for req in self.request_history
            if req["url"] == "/v2/spot/bids" and req["method"] == "POST"
        ]


def create_test_provider() -> tuple[FCPProvider, MockHTTPClient]:
    """Create FCP provider with mocked HTTP client.
    
    Returns both provider and mock for test assertions.
    """
    config = Config(
        provider="fcp",
        auth_token="test-token",
        provider_config={
            "project": "test-project",
            "region": DEFAULT_REGION,
            "ssh_keys": ["test-key"],
        }
    )
    
    mock_http = MockHTTPClient()
    provider = FCPProvider(config, http_client=mock_http)
    
    # Set up provider state to avoid external calls
    provider._project_id = DEFAULT_PROJECT_ID
    provider.ssh_key_manager._project_id = DEFAULT_PROJECT_ID
    
    return provider, mock_http


class TestFCPUserJourneys:
    """Test real user workflows with instance resolution.
    
    We mock ONLY the HTTP boundary - everything else runs real code.
    Each test is completely isolated.
    """

    def test_submit_job_with_friendly_instance_name(self):
        """Test that users can use 'a100' instead of FCP's internal ID."""
        provider, mock_http = create_test_provider()
        
        # What users actually do - use simple names
        config = TaskConfig(
            name="my-training",
            instance_type="a100",  # Simple name, not FCP's FID
            command=["python", "train.py"],
            upload_code=False,
        )

        # Submit task with user-friendly instance type
        task = provider.submit_task("a100", config)

        # Task should be created
        assert task.task_id.startswith("bid_")

        # Verify FCP received the correct FID, not "a100"
        bid_requests = mock_http.get_bid_creation_requests()
        assert len(bid_requests) == 1
        
        bid_payload = bid_requests[0]["kwargs"]["json"]
        assert bid_payload["instance_type"] == A100_FID, \
            "Provider should translate 'a100' to FCP's internal FID"

    def test_find_instances_with_count_prefix_format(self):
        """Test finding instances using count prefix format (e.g., 8xa100)."""
        provider, mock_http = create_test_provider()

        # User searches with friendly format
        instances = provider.find_instances({
            "instance_type": "8xa100",
            "region": DEFAULT_REGION,
        })

        # Verify API was called with correct FID
        availability_requests = [
            req for req in mock_http.request_history
            if req["url"] == "/v2/spot/availability"
        ]
        assert len(availability_requests) == 1
        
        request_params = availability_requests[0]["kwargs"]["params"]
        assert request_params["instance_type"] == A100_8X_FID, \
            "Provider should translate '8xa100' to FCP's internal FID"

        # Verify response shows human-readable name
        assert len(instances) == 1
        assert instances[0].instance_type == "a100-80gb.sxm.8x"
        assert instances[0].price_per_hour == 80.0

    def test_error_guidance_for_common_mistakes(self):
        """Test that common user mistakes get helpful error messages."""
        provider, mock_http = create_test_provider()

        # Common mistakes users might make
        mistake_configs = [
            ("nvidia-a100", "vendor-prefix"),
            ("A100", "capitalization"),
            ("gpu-a100", "wrong-prefix"),
            ("a100-gpu", "wrong-suffix"),
            ("totally-invalid", "completely-wrong"),
        ]

        for mistake, reason in mistake_configs:
            config = TaskConfig(
                name=f"test-{reason}",
                instance_type=mistake,
                command=["echo", "test"],
                upload_code=False,
            )

            with pytest.raises(FCPInstanceError) as exc_info:
                provider.submit_task(mistake, config)

            error = str(exc_info.value)
            
            # Error should be helpful
            assert "Unknown instance type:" in error, \
                f"Error should identify the problem for {reason}: {mistake}"
            assert mistake in error, \
                f"Error should mention the invalid type: {mistake}"
            assert "Available:" in error, \
                f"Error should list available options for {reason}: {mistake}"
            assert "a100" in error, \
                f"Error should include valid options for {reason}: {mistake}"

    def test_h100_instance_resolution(self):
        """Test H100 instance type resolution with multiple formats."""
        provider, mock_http = create_test_provider()

        # Test both H100 formats users might try
        test_formats = [
            ("8xh100", "count-prefix-format"),
            ("h100-80gb.sxm.8x", "full-fcp-format"),
            ("h100", "simple-name"),
        ]
        
        for instance_type, format_name in test_formats:
            # Clear request history for clean test
            mock_http.request_history.clear()
            
            config = TaskConfig(
                name=f"h100-test-{format_name}",
                instance_type=instance_type,
                command=["nvidia-smi"],
                upload_code=False,
            )

            task = provider.submit_task(instance_type, config)
            assert task.task_id.startswith("bid_")

            # Verify correct FID was used regardless of input format
            bid_requests = mock_http.get_bid_creation_requests()
            assert len(bid_requests) == 1
            
            bid_payload = bid_requests[0]["kwargs"]["json"]
            assert bid_payload["instance_type"] == H100_FID, \
                f"Failed to resolve {instance_type} to correct FID"

    def test_instance_resolution_with_region_filtering(self):
        """Test that instance resolution works with region constraints."""
        provider, mock_http = create_test_provider()
        
        # Search for instances in specific region
        instances = provider.find_instances({
            "instance_type": "a100",
            "region": DEFAULT_REGION,
            "max_price_per_hour": 100.0
        })
        
        assert len(instances) > 0, "Should find instances in specified region"
        
        # Verify all returned instances are in requested region
        for instance in instances:
            assert instance.region == DEFAULT_REGION, \
                f"Instance {instance.allocation_id} in wrong region"

    def test_instance_type_normalization(self):
        """Test that various instance type formats are normalized correctly."""
        provider, mock_http = create_test_provider()
        
        # Different ways users might specify the same instance
        equivalent_types = [
            "a100",
            "1xa100",  # Explicit count of 1
            "a100-80gb.sxm.1x",  # Full format
        ]
        
        for instance_type in equivalent_types:
            mock_http.request_history.clear()
            
            # Find instances
            instances = provider.find_instances({
                "instance_type": instance_type
            })
            
            # Should find the same instance
            assert len(instances) > 0
            assert instances[0].instance_type == "a100-80gb.sxm.1x", \
                f"Failed to normalize {instance_type}"

    def test_helpful_error_for_unavailable_instance_type(self):
        """Test error message when requested instance type is not available."""
        provider, mock_http = create_test_provider()
        
        # Try to find an instance type that's valid but not available
        instances = provider.find_instances({
            "instance_type": "a100",
            "max_price_per_hour": 0.01  # Unrealistically low price
        })
        
        # Should return empty list, not error
        assert instances == [], \
            "Should return empty list for valid but unavailable instance"

    def test_multiple_instance_task_submission(self):
        """Test submitting tasks to different instance types in sequence."""
        provider, mock_http = create_test_provider()
        
        instance_configs = [
            ("a100", "GPU training task"),
            ("8xa100", "Multi-GPU training"),
            ("h100", "H100 inference task"),
        ]
        
        submitted_tasks = []
        
        for instance_type, description in instance_configs:
            config = TaskConfig(
                name=f"test-{instance_type}",
                instance_type=instance_type,
                command=["echo", f"Running {description}"],
                upload_code=False,
            )
            
            task = provider.submit_task(instance_type, config)
            submitted_tasks.append((task, instance_type))
            
        # Verify all tasks were submitted
        assert len(submitted_tasks) == len(instance_configs)
        
        # Verify each task has unique ID
        task_ids = [task.task_id for task, _ in submitted_tasks]
        assert len(set(task_ids)) == len(task_ids), "Duplicate task IDs found"
        
        # Verify correct instance types were used
        bid_requests = mock_http.get_bid_creation_requests()
        assert len(bid_requests) == len(instance_configs)
        
        expected_fids = [A100_FID, A100_8X_FID, H100_FID]
        actual_fids = [req["kwargs"]["json"]["instance_type"] for req in bid_requests]
        assert actual_fids == expected_fids, "Instance types not resolved correctly"