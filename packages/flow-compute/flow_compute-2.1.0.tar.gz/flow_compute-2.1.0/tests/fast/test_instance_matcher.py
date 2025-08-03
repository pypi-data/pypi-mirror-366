"""Test instance matching logic."""

import pytest

from flow.core.resources.matcher import InstanceMatcher, NoMatchingInstanceError


class TestInstanceMatcher:
    """Test instance matching."""

    def setup_method(self):
        # Test catalog with various instances
        self.catalog = [
            {
                "instance_type": "a100.80gb.sxm4.1x",
                "gpu_type": "a100-80gb",
                "gpu_count": 1,
                "price_per_hour": 5.0,
                "available": True
            },
            {
                "instance_type": "a100.80gb.sxm4.4x",
                "gpu_type": "a100-80gb",
                "gpu_count": 4,
                "price_per_hour": 20.0,
                "available": True
            },
            {
                "instance_type": "a100.80gb.sxm4.8x",
                "gpu_type": "a100-80gb",
                "gpu_count": 8,
                "price_per_hour": 40.0,
                "available": False  # Not available
            },
            {
                "instance_type": "h100.80gb.sxm5.1x",
                "gpu_type": "h100-80gb",
                "gpu_count": 1,
                "price_per_hour": 10.0,
                "available": True
            },
            {
                "instance_type": "t4.16gb.pcie.1x",
                "gpu_type": "t4-16gb",
                "gpu_count": 1,
                "price_per_hour": 1.0,
                "available": True
            },
        ]
        self.matcher = InstanceMatcher(self.catalog)

    def test_exact_match(self):
        """Test exact GPU type and count match."""
        result = self.matcher.match({"gpu_type": "a100-80gb", "count": 1})
        assert result == "a100.80gb.sxm4.1x"

        result = self.matcher.match({"gpu_type": "a100-80gb", "count": 4})
        assert result == "a100.80gb.sxm4.4x"

    def test_larger_instance_fallback(self):
        """Test fallback to larger instance when exact match not available."""
        # Request 2 A100s, should get 4x instance
        result = self.matcher.match({"gpu_type": "a100-80gb", "count": 2})
        assert result == "a100.80gb.sxm4.4x"

    def test_unavailable_instance_skipped(self):
        """Test that unavailable instances are skipped."""
        # 8x A100 is unavailable, should fail
        with pytest.raises(NoMatchingInstanceError) as exc:
            self.matcher.match({"gpu_type": "a100-80gb", "count": 8})

        assert "No instances found with 8x a100-80gb" in str(exc.value)

    def test_no_matching_gpu_type(self):
        """Test error when GPU type doesn't exist."""
        with pytest.raises(NoMatchingInstanceError) as exc:
            self.matcher.match({"gpu_type": "v100-32gb", "count": 1})

        assert "No instances found with 1x v100-32gb" in str(exc.value)

    def test_case_insensitive_matching(self):
        """Test case insensitive GPU type matching."""
        result = self.matcher.match({"gpu_type": "A100-80GB", "count": 1})
        assert result == "a100.80gb.sxm4.1x"

    def test_suggestions_on_no_match(self):
        """Test helpful suggestions when no match found."""
        with pytest.raises(NoMatchingInstanceError) as exc:
            self.matcher.match({"gpu_type": "a100-80gb", "count": 16})

        error_str = str(exc.value)
        # Should show what's actually available
        assert "Available a100-80gb: a100.80gb.sxm4.1x (1 GPUs), a100.80gb.sxm4.4x (4 GPUs)" in error_str

    def test_empty_requirements(self):
        """Test handling of empty requirements."""
        # Should fail gracefully
        with pytest.raises(NoMatchingInstanceError):
            self.matcher.match({})
