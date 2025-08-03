"""Unit tests for FCP instance type mapping and resolution."""

import pytest
from unittest.mock import Mock, patch

from flow.providers.fcp.provider import FCPProvider
from flow.api.config import Config


class TestFCPInstanceTypeMapping:
    """Test instance type mapping logic in FCP provider."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock config
        self.config = Mock(spec=Config)
        self.config.provider = "fcp"
        self.config.provider_config = {}
        self.config.auth_token = "test-token"
        
        # Create mock HTTP client
        self.http_client = Mock()
        
        # Create provider instance
        self.provider = FCPProvider(self.config, self.http_client)

    def test_h100_instance_type_resolution(self):
        """Test that H100 instance types resolve to canonical 8xh100."""
        # Test that all H100 variants resolve to the same ID
        h100_variants = ["h100", "1xh100", "2xh100", "4xh100", "8xh100"]
        expected_id = "it_5ECSoHQjLBzrp5YM"
        
        for variant in h100_variants:
            resolved_id = self.provider._resolve_instance_type_simple(variant)
            assert resolved_id == expected_id, f"{variant} should resolve to {expected_id}"

    def test_get_instance_type_name_returns_canonical(self):
        """Test that instance type IDs map back to canonical names."""
        # H100 SXM should always return 8xh100
        h100_id = "it_5ECSoHQjLBzrp5YM"
        canonical_name = self.provider._get_instance_type_name(h100_id)
        assert canonical_name == "8xh100", f"H100 ID should map to '8xh100', got '{canonical_name}'"
        
        # H100 PCIe should return its full name
        h100_pcie_id = "it_XqgKWbhZ5gznAYsG"
        canonical_name = self.provider._get_instance_type_name(h100_pcie_id)
        assert canonical_name == "h100-80gb.pcie.8x", f"H100 PCIe ID should map correctly"

    def test_is_more_specific_type(self):
        """Test instance type specificity comparison."""
        # 8xh100 should be more specific than other H100 variants
        assert self.provider._is_more_specific_type("8xh100", "h100")
        assert self.provider._is_more_specific_type("8xh100", "1xh100")
        assert self.provider._is_more_specific_type("8xh100", "2xh100")
        assert self.provider._is_more_specific_type("8xh100", "4xh100")
        
        # h100-80gb.sxm.8x should not be more specific than 8xh100 for H100s
        assert not self.provider._is_more_specific_type("h100-80gb.sxm.8x", "8xh100")
        
        # Higher counts should be more specific
        assert self.provider._is_more_specific_type("4xa100", "2xa100")
        assert not self.provider._is_more_specific_type("2xa100", "4xa100")
        
        # Explicit counts are more specific than no count
        assert self.provider._is_more_specific_type("1xa100", "a100")
        assert not self.provider._is_more_specific_type("a100", "1xa100")

    def test_task_creation_uses_canonical_instance_type(self):
        """Test that task creation uses canonical instance type from FCP."""
        # Mock bid data with H100 instance
        bid_data = {
            "id": "bid_123",
            "instance_type": "it_5ECSoHQjLBzrp5YM",  # H100 ID
            "instance_quantity": 2,
            "status": "BID_OPEN",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Mock config that requested 2xh100
        config = Mock()
        config.instance_type = "2xh100"
        config.num_instances = 2
        
        # Create task from bid data
        task = self.provider._map_bid_to_task(bid_data, config)
        
        # Should use canonical 8xh100, not the requested 2xh100
        assert task.instance_type == "8xh100"
        assert task.num_instances == 2

    def test_unknown_instance_type_id(self):
        """Test handling of unknown instance type IDs."""
        unknown_id = "it_unknown123"
        result = self.provider._get_instance_type_name(unknown_id)
        # Should return the ID itself when unknown
        assert result == unknown_id

    def test_a100_instance_type_resolution(self):
        """Test A100 instance type resolution."""
        # Test various A100 formats
        a100_mappings = {
            "a100": "it_MsIRhxj3ccyVWGfP",
            "1xa100": "it_MsIRhxj3ccyVWGfP",
            "2xa100": "it_5M6aGxGovNeX5ltT",
            "4xa100": "it_fK7Cx6TVhOK5ZfXT",
            "8xa100": "it_J7OyNf9idfImLIFo",
        }
        
        for variant, expected_id in a100_mappings.items():
            resolved_id = self.provider._resolve_instance_type_simple(variant)
            assert resolved_id == expected_id, f"{variant} should resolve to {expected_id}"