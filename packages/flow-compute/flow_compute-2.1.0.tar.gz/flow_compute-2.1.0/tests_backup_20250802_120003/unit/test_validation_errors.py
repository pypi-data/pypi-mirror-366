"""Test validation error handling."""

import json
from unittest import TestCase
from unittest.mock import Mock

from flow.errors import ValidationAPIError


class TestValidationAPIError(TestCase):
    """Test ValidationAPIError formatting."""

    def test_parse_missing_field_errors(self):
        """Test parsing of missing field errors."""
        # Mock response with missing field errors
        response = Mock()
        response.status_code = 422
        response.text = '{"detail": [...]}'
        response.json.return_value = {
            "detail": [
                {"type": "missing", "loc": ["body", "project"], "msg": "Field required"},
                {"type": "missing", "loc": ["body", "region"], "msg": "Field required"},
                {"type": "missing", "loc": ["body", "disk_interface"], "msg": "Field required"}
            ]
        }

        error = ValidationAPIError(response)

        # Check error message formatting
        # Expected output based on centralized constants
        from flow.providers.fcp.core.constants import format_validation_help

        expected_lines = [
            "Validation failed:",
            "  - project: Field is required",
            "  - region: Field is required",
            "  - disk_interface: Field is required",
        ]

        # Add expected help for region
        expected_lines.append("")
        expected_lines.extend(format_validation_help("region"))

        # Add expected help for disk_interface
        expected_lines.append("")
        expected_lines.extend(format_validation_help("disk_interface"))
        assert error.args[0] == "\n".join(expected_lines)
        assert error.status_code == 422

    def test_parse_value_errors(self):
        """Test parsing of value errors."""
        response = Mock()
        response.status_code = 422
        response.text = '{"detail": [...]}'
        response.json.return_value = {
            "detail": [
                {"type": "value_error", "loc": ["body", "region"], "msg": "Invalid region 'us-east-1'"},
                {"type": "value_error", "loc": ["body", "size_gb"], "msg": "Must be greater than 0"}
            ]
        }

        error = ValidationAPIError(response)

        from flow.providers.fcp.core.constants import format_validation_help

        expected_lines = [
            "Validation failed:",
            "  - region: Invalid region 'us-east-1'",
            "  - size_gb: Must be greater than 0",
        ]

        # Add expected help for region
        expected_lines.append("")
        expected_lines.extend(format_validation_help("region"))
        assert error.args[0] == "\n".join(expected_lines)

    def test_nested_field_paths(self):
        """Test handling of nested field paths."""
        response = Mock()
        response.status_code = 422
        response.text = '{"detail": [...]}'
        response.json.return_value = {
            "detail": [
                {"type": "missing", "loc": ["body", "volumes", "0", "mount_path"], "msg": "Field required"}
            ]
        }

        error = ValidationAPIError(response)

        expected_lines = [
            "Validation failed:",
            "  - volumes.0.mount_path: Field is required"
        ]
        assert error.args[0] == "\n".join(expected_lines)

    def test_instance_type_error_hint(self):
        """Test that instance type errors get helpful hints."""
        response = Mock()
        response.status_code = 422
        response.text = '{"detail": [...]}'
        response.json.return_value = {
            "detail": [
                {"type": "value_error", "loc": ["body", "instance_type"], "msg": "Invalid instance type"}
            ]
        }

        error = ValidationAPIError(response)

        assert "Run 'flow instances' to see all available types" in error.args[0]

    def test_fallback_on_parse_error(self):
        """Test fallback when response isn't valid JSON."""
        response = Mock()
        response.status_code = 422
        response.text = 'Not JSON'
        response.json.side_effect = json.JSONDecodeError("msg", "doc", 0)

        error = ValidationAPIError(response)

        assert error.args[0] == "Validation failed. The request contained invalid data."
        assert error.response_body == "Not JSON"

    def test_empty_detail_list(self):
        """Test handling of empty detail list."""
        response = Mock()
        response.status_code = 422
        response.text = '{"detail": []}'
        response.json.return_value = {"detail": []}

        error = ValidationAPIError(response)

        assert error.args[0] == "Validation failed. The request contained invalid data."
