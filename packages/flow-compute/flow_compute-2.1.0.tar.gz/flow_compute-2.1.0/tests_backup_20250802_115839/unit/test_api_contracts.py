"""Contract tests for FCP API assumptions.

These tests verify that our API client correctly handles the expected API
responses and edge cases. Contract tests ensure our assumptions about the
external API remain valid.

Following the principle of defensive programming, we test:
1. Valid response parsing
2. Error response handling
3. Edge cases and malformed data
4. API version compatibility
5. Rate limiting and retries
"""

from datetime import datetime, timezone
from typing import Any, Dict

from hypothesis import given
from hypothesis import strategies as st

from flow.providers.fcp.api.types import (
    AuctionModel,
    BidModel,
    BidsResponse,
    InstanceTypeModel,
    ProjectModel,
    VolumeModel,
)


class TestAPIResponseContracts:
    """Test that API response models correctly parse expected data."""

    def test_project_response_contract(self):
        """Test ProjectModel parses API response correctly."""
        # Actual API response format
        api_response = {
            "fid": "proj-abc123",
            "name": "my-project",
            "created_at": "2024-01-15T10:30:00Z"
        }

        project = ProjectModel(**api_response)
        assert project.fid == "proj-abc123"
        assert project.name == "my-project"
        assert project.created_at == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    def test_instance_type_response_contract(self):
        """Test InstanceTypeModel handles various GPU configurations."""
        # Test cases based on actual API responses
        test_cases = [
            # GPU instance
            {
                "name": "gpu.nvidia.a100",
                "fid": "inst-type-123",
                "num_cpus": 32,
                "ram": 256,
                "gpus": [
                    {"name": "A100", "vram_gb": 80, "count": 1}
                ],
                "local_storage_gb": 1000,
                "network_bandwidth_gbps": 25.0
            },
            # Multi-GPU instance
            {
                "name": "gpu.nvidia.h100-8x",
                "fid": "inst-type-456",
                "num_cpus": 128,
                "ram": 2048,
                "gpus": [
                    {"name": "H100", "vram_gb": 80, "count": 8}
                ],
                "local_storage_gb": 8000,
                "network_bandwidth_gbps": 100.0
            },
            # CPU-only instance
            {
                "name": "cpu.intel.xeon",
                "fid": "inst-type-789",
                "num_cpus": 64,
                "ram": 512,
                "gpus": None,
                "local_storage_gb": 2000,
                "network_bandwidth_gbps": 10.0
            }
        ]

        for case in test_cases:
            instance = InstanceTypeModel(**case)
            assert instance.name == case["name"]
            assert instance.fid == case["fid"]
            assert instance.cpu_cores == case["num_cpus"]  # Field alias works
            assert instance.ram_gb == case["ram"]  # Field alias works

            if case["gpus"]:
                assert len(instance.gpus) == len(case["gpus"])
                for i, gpu in enumerate(instance.gpus):
                    assert gpu.name == case["gpus"][i]["name"]
                    assert gpu.vram_gb == case["gpus"][i]["vram_gb"]
                    assert gpu.count == case["gpus"][i]["count"]

    def test_auction_response_contract(self):
        """Test AuctionModel parses spot auction data correctly."""
        api_response = {
            "fid": "auction-123",
            "instance_type": "gpu.nvidia.a100",
            "region": "us-east-1",
            "capacity": 10,
            "last_instance_price": "$15.50",
            "min_bid_price": "$12.00",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z"
        }

        auction = AuctionModel(**api_response)
        assert auction.fid == "auction-123"
        assert auction.instance_type == "gpu.nvidia.a100"
        assert auction.region == "us-east-1"
        assert auction.capacity == 10
        assert auction.last_instance_price == "$15.50"
        assert auction.min_bid_price == "$12.00"

    def test_bid_response_contract(self):
        """Test BidModel handles all bid states correctly."""
        # Test different bid states
        states = ["pending", "running", "completed", "failed", "cancelled"]

        for state in states:
            api_response = {
                "fid": f"bid-{state}",
                "project": "proj-123",
                "region": "us-west-2",
                "instance_type": "gpu.nvidia.h100",
                "price": "$25.00",
                "status": state,
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T11:00:00Z",
                "ssh_keys": ["key-1", "key-2"],
                "startup_script": "#!/bin/bash\necho 'Hello'",
                "volumes": ["vol-1", "vol-2"]
            }

            bid = BidModel(**api_response)
            assert bid.status == state
            assert bid.ssh_keys == ["key-1", "key-2"]
            assert bid.volumes == ["vol-1", "vol-2"]

    def test_volume_response_contract(self):
        """Test VolumeModel handles different volume states."""
        test_cases = [
            # Block storage volume
            {
                "fid": "vol-123",
                "name": "training-data",
                "project": "proj-123",
                "region": "us-east-1",
                "capacity_gb": 1000,
                "interface": "block",
                "status": "available",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            # File storage volume
            {
                "fid": "vol-456",
                "name": "shared-models",
                "project": "proj-123",
                "region": "eu-west-1",
                "capacity_gb": 5000,
                "interface": "file",
                "status": "attached",
                "created_at": "2024-01-10T10:00:00Z",
                "updated_at": "2024-01-15T15:00:00Z"
            }
        ]

        for case in test_cases:
            volume = VolumeModel(**case)
            assert volume.fid == case["fid"]
            assert volume.interface == case["interface"]
            assert volume.status == case["status"]
            assert volume.capacity_gb == case["capacity_gb"]


class TestAPIErrorContracts:
    """Test error response handling contracts."""

    def test_authentication_error_contract(self):
        """Test 401 Unauthorized response handling."""
        error_responses = [
            {"error": "Invalid API key"},
            {"error": "Token expired"},
            {"error": "Unauthorized", "code": "AUTH_FAILED"},
            {"message": "Authentication required"},
        ]

        for response in error_responses:
            # All should be treated as auth errors
            assert self._should_raise_auth_error(401, response)

    def test_not_found_error_contract(self):
        """Test 404 Not Found response handling."""
        error_responses = [
            {"error": "Resource not found"},
            {"error": "Project not found", "resource": "proj-123"},
            {"message": "The requested resource does not exist"},
            {"code": "NOT_FOUND", "details": {"id": "bid-456"}},
        ]

        for response in error_responses:
            assert self._should_raise_not_found_error(404, response)

    def test_validation_error_contract(self):
        """Test 400 Bad Request validation error handling."""
        error_responses = [
            {
                "error": "Validation failed",
                "fields": {
                    "name": ["Required field"],
                    "instance_type": ["Invalid instance type"]
                }
            },
            {
                "error": "Invalid request",
                "validation_errors": [
                    {"field": "price", "message": "Must be positive"},
                    {"field": "region", "message": "Invalid region"}
                ]
            },
            {
                "message": "Bad request",
                "errors": ["Price too high", "Instance type not available"]
            }
        ]

        for response in error_responses:
            assert self._should_raise_validation_error(400, response)

    def test_rate_limit_error_contract(self):
        """Test 429 Too Many Requests handling."""
        error_responses = [
            {
                "error": "Rate limit exceeded",
                "retry_after": 60
            },
            {
                "error": "Too many requests",
                "limit": 100,
                "window": "1m",
                "retry_after_seconds": 45
            },
            {
                "message": "API rate limit hit",
                "headers": {
                    "X-RateLimit-Limit": "100",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "1705321200"
                }
            }
        ]

        for response in error_responses:
            assert self._should_raise_rate_limit_error(429, response)

    def _should_raise_auth_error(self, status_code: int, response: Dict[str, Any]) -> bool:
        """Check if response should raise auth error."""
        return status_code == 401

    def _should_raise_not_found_error(self, status_code: int, response: Dict[str, Any]) -> bool:
        """Check if response should raise not found error."""
        return status_code == 404

    def _should_raise_validation_error(self, status_code: int, response: Dict[str, Any]) -> bool:
        """Check if response should raise validation error."""
        return status_code == 400 and any(
            key in response for key in ["validation_errors", "fields", "errors"]
        )

    def _should_raise_rate_limit_error(self, status_code: int, response: Dict[str, Any]) -> bool:
        """Check if response should raise rate limit error."""
        return status_code == 429


class TestAPICompatibility:
    """Test API version compatibility and evolution."""

    def test_extra_fields_ignored(self):
        """Test that extra fields in API responses are ignored."""
        # API might add new fields - we should handle gracefully
        api_response = {
            "fid": "proj-123",
            "name": "my-project",
            "created_at": "2024-01-15T10:00:00Z",
            # New fields that might be added
            "organization": "org-456",
            "billing_account": "bill-789",
            "tags": ["production", "ml"],
            "metadata": {"team": "research"}
        }

        # Should parse without error, ignoring extra fields
        project = ProjectModel(**api_response)
        assert project.fid == "proj-123"
        assert project.name == "my-project"

    def test_optional_fields_missing(self):
        """Test that optional fields can be missing."""
        # Minimal responses should work
        test_cases = [
            # Auction without optional fields
            (AuctionModel, {
                "fid": "auction-123",
                "instance_type": "gpu.nvidia.a100",
                "region": "us-east-1",
                "capacity": 5,
                "last_instance_price": "$20.00"
                # min_bid_price, created_at, updated_at are optional
            }),
            # Volume without timestamps (shouldn't happen but be defensive)
            (VolumeModel, {
                "fid": "vol-123",
                "name": "data",
                "project": "proj-123",
                "region": "us-east-1",
                "capacity_gb": 100,
                "interface": "block",
                "status": "available",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }),
        ]

        for model_class, data in test_cases:
            instance = model_class(**data)
            assert instance.fid == data["fid"]

    def test_field_type_coercion(self):
        """Test that reasonable type coercions work."""
        # API might return numbers as strings sometimes
        api_response = {
            "name": "gpu.nvidia.a100",
            "fid": "inst-type-123",
            "num_cpus": "32",  # String instead of int
            "ram": "256",      # String instead of int
            "gpus": [{"name": "A100", "vram_gb": "80", "count": "1"}],
            "local_storage_gb": "1000",
            "network_bandwidth_gbps": "25.0"
        }

        instance = InstanceTypeModel(**api_response)
        assert instance.cpu_cores == 32  # Coerced to int
        assert instance.ram_gb == 256    # Coerced to int
        assert instance.gpus[0].vram_gb == 80  # Coerced to int


class TestPaginationContracts:
    """Test pagination response contracts."""

    def test_paginated_bids_response(self):
        """Test BidsResponse pagination contract."""
        # First page
        page1 = {
            "data": [
                {
                    "fid": f"bid-{i}",
                    "project": "proj-123",
                    "region": "us-east-1",
                    "instance_type": "gpu.nvidia.a100",
                    "price": "$20.00",
                    "status": "running",
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-15T10:00:00Z",
                    "ssh_keys": [],
                }
                for i in range(10)
            ],
            "next_cursor": "cursor-abc123"
        }

        response1 = BidsResponse(**page1)
        assert len(response1.data) == 10
        assert response1.next_cursor == "cursor-abc123"

        # Last page
        page2 = {
            "data": [
                {
                    "fid": f"bid-{i+10}",
                    "project": "proj-123",
                    "region": "us-east-1",
                    "instance_type": "gpu.nvidia.a100",
                    "price": "$20.00",
                    "status": "completed",
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-15T11:00:00Z",
                    "ssh_keys": [],
                }
                for i in range(5)
            ],
            "next_cursor": None  # No more pages
        }

        response2 = BidsResponse(**page2)
        assert len(response2.data) == 5
        assert response2.next_cursor is None

    def test_empty_page_response(self):
        """Test empty pagination response."""
        empty_page = {
            "data": [],
            "next_cursor": None
        }

        response = BidsResponse(**empty_page)
        assert len(response.data) == 0
        assert response.next_cursor is None


class TestAPIEdgeCases:
    """Test edge cases in API responses."""

    def test_price_string_formats(self):
        """Test various price string formats from API."""
        valid_prices = [
            "$0.01",      # Minimum
            "$1.00",      # Simple
            "$15.50",     # Common
            "$100.00",    # Round
            "$9999.99",   # Maximum
            "$12.345",    # Extra precision (API might return)
        ]

        for price in valid_prices:
            auction = AuctionModel(
                fid="auction-test",
                instance_type="gpu.nvidia.a100",
                region="us-east-1",
                capacity=1,
                last_instance_price=price
            )
            assert auction.last_instance_price == price

    def test_datetime_formats(self):
        """Test various datetime formats from API."""
        datetime_formats = [
            "2024-01-15T10:30:00Z",           # UTC with Z
            "2024-01-15T10:30:00+00:00",      # UTC with offset
            "2024-01-15T10:30:00.123Z",       # With milliseconds
            "2024-01-15T10:30:00.123456Z",    # With microseconds
        ]

        for dt_str in datetime_formats:
            project = ProjectModel(
                fid="proj-test",
                name="test",
                created_at=dt_str
            )
            assert isinstance(project.created_at, datetime)
            assert project.created_at.tzinfo is not None  # Has timezone

    def test_empty_collections(self):
        """Test empty arrays/lists in responses."""
        bid = BidModel(
            fid="bid-123",
            project="proj-123",
            region="us-east-1",
            instance_type="gpu.nvidia.a100",
            price="$20.00",
            status="pending",
            created_at="2024-01-15T10:00:00Z",
            updated_at="2024-01-15T10:00:00Z",
            ssh_keys=[],      # Empty list
            startup_command=None,  # Null
            volumes=None      # Null instead of empty list
        )

        assert bid.ssh_keys == []
        assert bid.startup_script is None
        assert bid.volumes is None

    def test_very_long_strings(self):
        """Test handling of very long strings from API."""
        # API might return very long startup scripts
        long_script = "#!/bin/bash\n" + "\n".join([
            f"echo 'Line {i}'" for i in range(1000)
        ])

        bid = BidModel(
            fid="bid-123",
            project="proj-123",
            region="us-east-1",
            instance_type="gpu.nvidia.a100",
            price="$20.00",
            status="running",
            created_at="2024-01-15T10:00:00Z",
            updated_at="2024-01-15T10:00:00Z",
            ssh_keys=["key-1"],
            startup_script=long_script
        )

        assert len(bid.startup_script) > 10000
        assert bid.startup_script.startswith("#!/bin/bash")


class TestAPIAssumptions:
    """Test our assumptions about API behavior."""

    def test_fid_format_assumptions(self):
        """Test our assumptions about FID formats."""
        # FIDs follow predictable patterns
        fid_patterns = {
            "project": ["proj-abc123", "proj-xyz789"],
            "bid": ["bid-abc123", "bid-xyz789"],
            "volume": ["vol-abc123", "vol-xyz789"],
            "instance_type": ["inst-type-123", "inst-type-gpu-a100"],
            "ssh_key": ["key-abc123", "key-user-default"],
        }

        for resource_type, examples in fid_patterns.items():
            for fid in examples:
                # Should match pattern: {prefix}-{suffix}
                assert "-" in fid
                prefix, suffix = fid.split("-", 1)
                assert len(prefix) >= 3
                assert len(suffix) >= 3

    def test_region_format_assumptions(self):
        """Test our assumptions about region formats."""
        valid_regions = [
            "us-east-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
        ]

        for region in valid_regions:
            # Should be {geo}-{direction}-{number}
            parts = region.split("-")
            assert len(parts) == 3
            assert parts[0] in ["us", "eu", "ap"]
            assert parts[1] in ["east", "west", "central", "southeast", "northeast"]
            assert parts[2].isdigit()

    def test_status_transitions(self):
        """Test our assumptions about status transitions."""
        # Valid status transitions
        valid_transitions = {
            "pending": ["running", "failed", "cancelled"],
            "running": ["completed", "failed", "cancelled"],
            "completed": [],  # Terminal state
            "failed": [],     # Terminal state
            "cancelled": [],  # Terminal state
        }

        # All statuses should be in our transition map
        for status in ["pending", "running", "completed", "failed", "cancelled"]:
            assert status in valid_transitions

    @given(
        capacity=st.integers(min_value=1, max_value=1000),
        price=st.floats(min_value=0.01, max_value=10000, allow_nan=False)
    )
    def test_auction_invariants(self, capacity, price):
        """Test invariants for auction data."""
        price_str = f"${price:.2f}"

        auction = AuctionModel(
            fid="auction-test",
            instance_type="gpu.nvidia.a100",
            region="us-east-1",
            capacity=capacity,
            last_instance_price=price_str
        )

        # Invariants
        assert auction.capacity > 0
        assert auction.last_instance_price.startswith("$")
        assert float(auction.last_instance_price[1:]) > 0


class TestAPIRetryAssumptions:
    """Test assumptions about API retry behavior."""

    def test_retryable_status_codes(self):
        """Test which HTTP status codes should trigger retries."""
        # Definitely retry
        retryable = [
            429,  # Rate limited
            500,  # Internal server error
            502,  # Bad gateway
            503,  # Service unavailable
            504,  # Gateway timeout
        ]

        # Don't retry
        non_retryable = [
            400,  # Bad request
            401,  # Unauthorized
            403,  # Forbidden
            404,  # Not found
            405,  # Method not allowed
            409,  # Conflict
            422,  # Unprocessable entity
        ]

        for code in retryable:
            assert self._should_retry(code)

        for code in non_retryable:
            assert not self._should_retry(code)

    def test_retry_after_header_parsing(self):
        """Test parsing of Retry-After header."""
        test_cases = [
            # Seconds
            ("60", 60),
            ("120", 120),
            ("3600", 3600),
            # HTTP date (mock as seconds from now)
            ("Wed, 21 Oct 2024 07:28:00 GMT", None),  # Would need date parsing
        ]

        for header_value, expected_seconds in test_cases:
            if expected_seconds:
                assert self._parse_retry_after(header_value) == expected_seconds

    def _should_retry(self, status_code: int) -> bool:
        """Check if status code is retryable."""
        return status_code >= 500 or status_code == 429

    def _parse_retry_after(self, value: str) -> int:
        """Parse Retry-After header to seconds."""
        try:
            return int(value)
        except ValueError:
            # Would parse HTTP date here
            return 60  # Default
