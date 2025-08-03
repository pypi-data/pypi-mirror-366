"""Tests for invoke module serialization error handling."""

import pytest

from flow.api.invoke import _serialize_to_json


class TestInvokeSerializationErrors:
    """Test serialization error handling in invoke module."""

    def test_serialize_to_json_with_custom_object(self):
        """Test helpful error when serializing custom objects."""
        class MyModel:
            def __init__(self):
                self.weights = [1, 2, 3]

        model = MyModel()

        with pytest.raises(TypeError) as exc_info:
            _serialize_to_json(model, "model argument")

        error_msg = str(exc_info.value)
        assert "Cannot serialize model argument to JSON" in error_msg
        assert "MyModel" in error_msg
        # Our improved error message gives type-specific help
        assert "pickle.dump() or convert to dict" in error_msg  # For generic objects
        assert "JSON only supports" in error_msg

    def test_serialize_to_json_with_bytes(self):
        """Test error message for bytes objects."""
        data = b"binary data"

        with pytest.raises(TypeError) as exc_info:
            _serialize_to_json(data, "binary data")

        error_msg = str(exc_info.value)
        assert "Cannot serialize binary data to JSON" in error_msg
        assert "bytes" in error_msg

    def test_serialize_to_json_with_set(self):
        """Test error message for set objects."""
        data = {1, 2, 3}

        with pytest.raises(TypeError) as exc_info:
            _serialize_to_json(data, "set argument")

        error_msg = str(exc_info.value)
        assert "Cannot serialize set argument to JSON" in error_msg
        assert "set" in error_msg

    def test_serialize_to_json_success(self):
        """Test successful serialization of valid types."""
        # All these should work
        assert _serialize_to_json({"a": 1}, "dict") == '{"a": 1}'
        assert _serialize_to_json([1, 2, 3], "list") == '[1, 2, 3]'
        assert _serialize_to_json("hello", "string") == '"hello"'
        assert _serialize_to_json(42, "number") == '42'
        assert _serialize_to_json(3.14, "float") == '3.14'
        assert _serialize_to_json(True, "bool") == 'true'
        assert _serialize_to_json(None, "null") == 'null'

    def test_serialize_to_json_shows_value_preview(self):
        """Test that error shows a preview of the problematic value."""
        class LongObject:
            def __repr__(self):
                return "A" * 200  # Long repr

        obj = LongObject()
        with pytest.raises(TypeError) as exc_info:
            _serialize_to_json(obj, "long object")

        error_msg = str(exc_info.value)
        assert "Value: " + "A" * 100 + "..." in error_msg  # Should truncate at 100 chars
