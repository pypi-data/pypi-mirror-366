"""Test GPU string parsing."""

import pytest

from flow.core.resources.parser import GPUParser
from flow.errors import ValidationError


class TestGPUParser:
    """Test GPU string parsing."""

    def setup_method(self):
        self.parser = GPUParser()

    def test_simple_gpu_type(self):
        """Test parsing simple GPU type."""
        result = self.parser.parse("a100")
        assert result == {"gpu_type": "a100-80gb", "count": 1}

    def test_gpu_with_count(self):
        """Test parsing GPU with count."""
        result = self.parser.parse("a100:4")
        assert result == {"gpu_type": "a100-80gb", "count": 4}

    def test_all_supported_gpus(self):
        """Test all supported GPU types."""
        gpu_types = {
            "a100": "a100-80gb",
            "h100": "h100-80gb",
            "a10": "a10-24gb",
            "t4": "t4-16gb",
            "v100": "v100-32gb",
            "l4": "l4-24gb"
        }

        for short_name, canonical in gpu_types.items():
            result = self.parser.parse(short_name)
            assert result == {"gpu_type": canonical, "count": 1}

    def test_case_insensitive(self):
        """Test case insensitive parsing."""
        assert self.parser.parse("A100") == {"gpu_type": "a100-80gb", "count": 1}
        assert self.parser.parse("H100:2") == {"gpu_type": "h100-80gb", "count": 2}

    def test_empty_string(self):
        """Test empty string returns empty dict."""
        assert self.parser.parse("") == {}

    def test_invalid_format(self):
        """Test invalid format raises error."""
        with pytest.raises(ValidationError) as exc:
            self.parser.parse("invalid::format")

        # Check suggestions
        assert "Use format: 'a100' or 'a100:4'" in str(exc.value)

    def test_unknown_gpu(self):
        """Test unknown GPU type."""
        with pytest.raises(ValidationError) as exc:
            self.parser.parse("rtx4090")

        assert "Unknown GPU type: rtx4090" in str(exc.value)
        assert "Supported GPUs:" in str(exc.value)

    def test_invalid_count_too_small(self):
        """Test GPU count validation - too small."""
        with pytest.raises(ValidationError) as exc:
            self.parser.parse("a100:0")

        assert "Invalid GPU count: 0" in str(exc.value)
        assert "GPU count must be between 1 and 8" in str(exc.value)

    def test_invalid_count_too_large(self):
        """Test GPU count validation - too large."""
        with pytest.raises(ValidationError) as exc:
            self.parser.parse("a100:16")

        assert "Invalid GPU count: 16" in str(exc.value)
        assert "GPU count must be between 1 and 8" in str(exc.value)

    def test_max_valid_count(self):
        """Test maximum valid GPU count."""
        result = self.parser.parse("h100:8")
        assert result == {"gpu_type": "h100-80gb", "count": 8}
