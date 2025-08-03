"""Test the invoke module for remote function execution."""

import json
import tempfile
from pathlib import Path

import pytest

from flow.api.invoke import _create_invoke_script, _parse_invoke_result


class TestInvokeIntegration:
    """Test remote function invocation functionality."""

    def test_invoke_script_generation(self):
        """Test invoke script generation without mocking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test module
            module_path = Path(temp_dir) / "test_module.py"
            module_path.write_text("""
def add(x, y):
    return x + y

def multiply(x, y, scale=1):
    return x * y * scale
""")

            # Test simple function with positional args
            script = _create_invoke_script(
                module_path=str(module_path),
                function_name="add",
                args=[1, 2],
                kwargs={},
                result_path="/tmp/result.json",
                temp_dir=temp_dir
            )

            assert "import sys" in script
            assert "importlib.util" in script
            assert 'spec_from_file_location("user_module"' in script
            assert "func = getattr(module, function_name)" in script
            assert "result = func(*args, **kwargs)" in script
            assert "json.dumps(result)" in script

            # Test function with kwargs
            script = _create_invoke_script(
                module_path=str(module_path),
                function_name="multiply",
                args=[3, 4],
                kwargs={"scale": 2},
                result_path="/tmp/result.json",
                temp_dir=temp_dir
            )

            assert 'function_name = \'multiply\'' in script
            assert "args = [3, 4]" in script
            assert 'kwargs = {"scale": 2}' in script

    @pytest.mark.parametrize("test_data,expected", [
        # Simple types
        (42, 42),
        ("hello", "hello"),
        (3.14, 3.14),
        (True, True),
        (None, None),

        # Collections
        ([1, 2, 3], [1, 2, 3]),
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        ((1, 2), [1, 2]),  # Tuples become lists in JSON

        # Nested structures
        ({"data": [1, 2, {"nested": True}]}, {"data": [1, 2, {"nested": True}]}),

        # Edge cases
        ([], []),
        ({}, {}),
        ("", ""),
        (0, 0),
        (False, False),
    ])
    def test_result_serialization_roundtrip(self, test_data, expected):
        """Test serialization/deserialization of various result types."""
        # Simulate what happens in the invoke script
        json_result = json.dumps(test_data)

        # Parse the result
        parsed = _parse_invoke_result(json_result)

        assert parsed == expected

    def test_invoke_error_handling(self):
        """Test error handling in invoke operations."""
        # Test invalid JSON
        with pytest.raises(json.JSONDecodeError):
            _parse_invoke_result("not valid json")

        # Test empty result
        with pytest.raises(json.JSONDecodeError):
            _parse_invoke_result("")

        # Test script generation with invalid paths
        script = _create_invoke_script(
            module_path="/nonexistent/module.py",
            function_name="func",
            args=[],
            kwargs={},
            result_path="/tmp/result.json"
        )

        # Script should still be generated (execution will fail)
        assert 'module_path = \'/nonexistent/module.py\'' in script
        assert 'function_name = \'func\'' in script
        assert "args = []" in script

        # Test with very long result path (potential truncation)
        long_path = "/tmp/" + "a" * 1000 + "/result.json"
        script = _create_invoke_script(
            module_path="module.py",
            function_name="func",
            args=[],
            kwargs={},
            result_path=long_path,
            max_result_size=100  # Small limit
        )

        assert str(100) in script  # max_result_size should be in script
