"""Comprehensive unit tests for the invoke module.

Tests cover all edge cases, error scenarios, and ensure robust behavior
following the principles of thorough testing and defensive programming.
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch, MagicMock
import pytest

from flow.api.invoke import (
    _serialize_to_json,
    _create_invoke_script,
    _parse_invoke_result,
    InvokeTask,
    invoke,
    invoke_async,
)
from flow.errors import TaskExecutionError, InvalidResponseError, ValidationError


class TestSerializeToJson:
    """Comprehensive tests for JSON serialization with edge cases."""

    def test_basic_types_serialization(self):
        """Test serialization of all basic JSON-compatible types."""
        # Primitives
        assert _serialize_to_json(42, "int") == "42"
        assert _serialize_to_json(3.14159, "float") == "3.14159"
        assert _serialize_to_json("hello", "str") == '"hello"'
        assert _serialize_to_json(True, "bool") == "true"
        assert _serialize_to_json(False, "bool") == "false"
        assert _serialize_to_json(None, "none") == "null"
        
        # Collections
        assert _serialize_to_json([1, 2, 3], "list") == "[1, 2, 3]"
        assert _serialize_to_json({"a": 1, "b": 2}, "dict") == '{"a": 1, "b": 2}'
        assert _serialize_to_json((1, 2, 3), "tuple") == "[1, 2, 3]"  # Tuples become lists
        
    def test_nested_structures(self):
        """Test deeply nested data structures."""
        nested = {
            "level1": {
                "level2": {
                    "level3": [1, 2, {"level4": "deep"}]
                }
            },
            "array": [[1, 2], [3, 4], [{"nested": True}]]
        }
        result = _serialize_to_json(nested, "nested structure")
        parsed = json.loads(result)
        assert parsed == nested
        
    def test_edge_case_values(self):
        """Test edge case values."""
        # Empty collections
        assert _serialize_to_json([], "empty list") == "[]"
        assert _serialize_to_json({}, "empty dict") == "{}"
        assert _serialize_to_json("", "empty string") == '""'
        
        # Large numbers
        assert _serialize_to_json(10**100, "large int") == str(10**100)
        assert _serialize_to_json(-10**100, "negative large int") == str(-10**100)
        
        # Special floats
        assert _serialize_to_json(float('inf'), "infinity") == "Infinity"
        assert _serialize_to_json(float('-inf'), "negative infinity") == "-Infinity"
        # NaN is tricky - json.dumps converts it to NaN but it's not valid JSON
        
    def test_unicode_and_special_characters(self):
        """Test Unicode and special character handling."""
        unicode_data = {
            "emoji": "🚀🔥💻",
            "chinese": "你好世界",
            "arabic": "مرحبا بالعالم",
            "special": "tab\ttab\nnewline\r\nwindows",
            "quotes": 'He said "Hello"',
            "backslash": "path\\to\\file"
        }
        result = _serialize_to_json(unicode_data, "unicode data")
        parsed = json.loads(result)
        assert parsed == unicode_data
        
    def test_custom_objects_with_helpful_errors(self):
        """Test error messages for various non-serializable types."""
        # Custom class
        class CustomModel:
            def __init__(self):
                self.data = "internal"
                
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(CustomModel(), "model")
        assert "Cannot serialize model to JSON" in str(exc.value)
        assert "CustomModel" in str(exc.value)
        assert "pickle.dump() or convert to dict" in str(exc.value)
        
        # Mock numpy array
        class FakeNumpyArray:
            def __init__(self):
                self.__class__.__name__ = "ndarray"
                
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(FakeNumpyArray(), "array")
        assert "np.save('/tmp/data.npy', obj)" in str(exc.value)
        
        # Mock pandas DataFrame
        class FakeDataFrame:
            def __init__(self):
                self.__class__.__name__ = "DataFrame"
                
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(FakeDataFrame(), "dataframe")
        assert "df.to_parquet('/tmp/data.parquet')" in str(exc.value)
        
        # Mock PyTorch tensor
        class FakeTensor:
            def __init__(self):
                self.__class__.__name__ = "Tensor"
                
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(FakeTensor(), "tensor")
        assert "torch.save(obj, '/tmp/model.pt')" in str(exc.value)
        
    def test_very_long_repr_truncation(self):
        """Test that very long repr strings are truncated in errors."""
        class VeryLongRepr:
            def __repr__(self):
                return "X" * 200
                
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(VeryLongRepr(), "long object")
        error_msg = str(exc.value)
        assert ("X" * 100 + "...") in error_msg
        assert "X" * 101 not in error_msg  # Should be truncated
        
    def test_circular_references(self):
        """Test handling of circular references."""
        # Create circular reference
        circular = {"a": 1}
        circular["self"] = circular
        
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(circular, "circular data")
        assert "Cannot serialize circular data to JSON" in str(exc.value)
            
    def test_bytes_and_bytearray(self):
        """Test bytes and bytearray error handling."""
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(b"binary data", "bytes")
        assert "Cannot serialize bytes to JSON" in str(exc.value)
        
        with pytest.raises(TypeError) as exc:
            _serialize_to_json(bytearray(b"binary"), "bytearray")
        assert "Cannot serialize bytearray to JSON" in str(exc.value)


class TestCreateInvokeScript:
    """Tests for invoke script generation."""
    
    def test_basic_script_generation(self):
        """Test basic script generation with minimal parameters."""
        script = _create_invoke_script(
            module_path="/path/to/module.py",
            function_name="process",
            args=[],
            kwargs={},
            result_path="/tmp/result.json"
        )
        
        # Check key components
        assert "import sys" in script
        assert "import json" in script
        assert "import importlib.util" in script
        assert 'module_path = \'/path/to/module.py\'' in script
        assert 'function_name = \'process\'' in script
        assert 'args = []' in script
        assert 'kwargs = {}' in script
        assert 'result_path = \'/tmp/result.json\'' in script
        assert 'spec_from_file_location("user_module"' in script
        assert 'func = getattr(module, function_name)' in script
        assert 'result = func(*args, **kwargs)' in script
        
    def test_script_with_complex_parameters(self):
        """Test script generation with complex args and kwargs."""
        script = _create_invoke_script(
            module_path="/src/ml/train.py",
            function_name="train_model",
            args=["data.csv", 100, True],
            kwargs={"learning_rate": 0.001, "batch_size": 32, "optimizer": "adam"},
            result_path="/tmp/training_result.json",
            max_result_size=50 * 1024 * 1024  # 50MB
        )
        
        assert 'args = ["data.csv", 100, true]' in script  # Note: True -> true in JSON
        assert '"learning_rate": 0.001' in script
        assert '"batch_size": 32' in script
        assert '"optimizer": "adam"' in script
        assert 'max_result_size = 52428800' in script  # 50MB in bytes
        
    def test_script_with_cleanup(self):
        """Test async script generation with cleanup."""
        script = _create_invoke_script(
            module_path="/module.py",
            function_name="func",
            args=[],
            kwargs={},
            result_path="/tmp/result.json",
            temp_dir="/tmp/flow-invoke-abc123"
        )
        
        # Check cleanup components
        assert 'temp_dir = \'/tmp/flow-invoke-abc123\'' in script
        assert 'def cleanup():' in script
        assert 'shutil.rmtree(temp_dir)' in script
        assert 'cleanup()' in script  # Should be called on error
        
    def test_script_error_handling(self):
        """Test error handling in generated script."""
        script = _create_invoke_script(
            module_path="/test.py",
            function_name="test",
            args=[],
            kwargs={},
            result_path="/tmp/result.json"
        )
        
        # Check error handling
        assert 'if not spec or not spec.loader:' in script
        assert 'if not hasattr(module, function_name):' in script
        assert 'except Exception as e:' in script
        assert 'traceback.print_exc()' in script
        assert 'sys.exit(1)' in script
        
    def test_special_characters_in_paths(self):
        """Test handling of special characters in paths."""
        script = _create_invoke_script(
            module_path="/path with spaces/module.py",
            function_name="func_name",
            args=[],
            kwargs={},
            result_path="/tmp/result with spaces.json"
        )
        
        # repr() should properly escape the paths
        assert "'/path with spaces/module.py'" in script
        assert "'/tmp/result with spaces.json'" in script
        
    def test_result_size_checking(self):
        """Test result size limit checking in script."""
        script = _create_invoke_script(
            module_path="/test.py",
            function_name="test",
            args=[],
            kwargs={},
            result_path="/tmp/result.json",
            max_result_size=1024  # 1KB limit
        )
        
        assert 'max_result_size = 1024' in script
        assert 'result_size = len(result_json.encode(\'utf-8\'))' in script
        assert 'if result_size > max_result_size:' in script
        assert 'Result too large' in script


class TestParseInvokeResult:
    """Tests for result parsing."""
    
    def test_parse_valid_json(self):
        """Test parsing of various valid JSON results."""
        # Simple values
        assert _parse_invoke_result('42') == 42
        assert _parse_invoke_result('"hello"') == "hello"
        assert _parse_invoke_result('true') == True
        assert _parse_invoke_result('null') is None
        
        # Complex structures
        assert _parse_invoke_result('{"a": 1, "b": [2, 3]}') == {"a": 1, "b": [2, 3]}
        assert _parse_invoke_result('[1, 2, 3]') == [1, 2, 3]
        
    def test_parse_invalid_json(self):
        """Test error handling for invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            _parse_invoke_result("not json")
            
        with pytest.raises(json.JSONDecodeError):
            _parse_invoke_result("{incomplete")
            
        with pytest.raises(json.JSONDecodeError):
            _parse_invoke_result("")
            
        with pytest.raises(json.JSONDecodeError):
            _parse_invoke_result("{'single': 'quotes'}")  # JSON requires double quotes
            
    def test_parse_edge_cases(self):
        """Test parsing edge cases."""
        # Very large numbers
        large_num = str(10**100)
        assert _parse_invoke_result(large_num) == 10**100
        
        # Unicode
        assert _parse_invoke_result('"🚀"') == "🚀"
        assert _parse_invoke_result('{"emoji": "🔥"}') == {"emoji": "🔥"}
        
        # Escaped characters
        assert _parse_invoke_result('"line1\\nline2"') == "line1\nline2"
        assert _parse_invoke_result('"tab\\ttab"') == "tab\ttab"


class TestInvokeTask:
    """Tests for InvokeTask class."""
    
    def test_invoke_task_initialization(self):
        """Test InvokeTask initialization."""
        mock_task = Mock()
        mock_task.task_id = "test-123"
        result_path = Path("/tmp/result.json")
        temp_dir = Path("/tmp/flow-invoke-test")
        
        invoke_task = InvokeTask(mock_task, result_path, temp_dir)
        
        assert invoke_task.task == mock_task
        assert invoke_task._result_path == result_path
        assert invoke_task._temp_dir == temp_dir
        assert invoke_task._result_cached is None
        assert invoke_task._cleaned_up is False
        
    def test_get_result_success(self):
        """Test successful result retrieval."""
        # Setup
        mock_task = Mock()
        mock_task.status = "completed"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "result.json"
            result_data = {"accuracy": 0.95, "loss": 0.01}
            result_path.write_text(json.dumps(result_data))
            
            invoke_task = InvokeTask(mock_task, result_path, Path(temp_dir))
            
            # First call should read from file
            result = invoke_task.get_result()
            assert result == result_data
            
            # Second call should use cache
            # Don't delete file, just verify cache is used
            result2 = invoke_task.get_result()
            assert result2 == result_data
            
    def test_get_result_task_not_complete(self):
        """Test error when trying to get result before task completes."""
        mock_task = Mock()
        mock_task.status = "running"
        
        invoke_task = InvokeTask(mock_task, Path("/tmp/result.json"), Path("/tmp"))
        
        with pytest.raises(TaskExecutionError) as exc:
            invoke_task.get_result()
        assert "Cannot get result, task is running" in str(exc.value)
        assert "Call task.wait() first" in str(exc.value)
        
    def test_get_result_task_failed(self):
        """Test error when task failed."""
        mock_task = Mock()
        mock_task.status = "failed"
        
        invoke_task = InvokeTask(mock_task, Path("/tmp/result.json"), Path("/tmp"))
        
        with pytest.raises(TaskExecutionError) as exc:
            invoke_task.get_result()
        assert "Task failed during execution" in str(exc.value)
        assert "Check task logs with task.logs()" in str(exc.value)
        
    def test_get_result_file_not_found(self):
        """Test error when result file is missing."""
        mock_task = Mock()
        mock_task.status = "completed"
        
        invoke_task = InvokeTask(
            mock_task, 
            Path("/tmp/nonexistent-result.json"), 
            Path("/tmp")
        )
        
        with pytest.raises(TaskExecutionError) as exc:
            invoke_task.get_result()
        assert "Result file not found" in str(exc.value)
        
    def test_get_result_invalid_json(self):
        """Test error when result file contains invalid JSON."""
        mock_task = Mock()
        mock_task.status = "completed"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "result.json"
            result_path.write_text("not valid json")
            
            invoke_task = InvokeTask(mock_task, result_path, Path(temp_dir))
            
            with pytest.raises(InvalidResponseError) as exc:
                invoke_task.get_result()
            assert "Failed to parse result JSON" in str(exc.value)
            
    def test_cleanup_behavior(self):
        """Test cleanup is called properly."""
        mock_task = Mock()
        mock_task.status = "completed"
        
        with tempfile.TemporaryDirectory() as base_dir:
            temp_dir = Path(base_dir) / "flow-invoke-test"
            temp_dir.mkdir()
            result_path = temp_dir / "result.json"
            result_path.write_text('{"result": "data"}')
            
            # Create a test file to verify cleanup
            test_file = temp_dir / "test.txt"
            test_file.write_text("test")
            
            invoke_task = InvokeTask(mock_task, result_path, temp_dir)
            
            # Verify directory exists
            assert temp_dir.exists()
            assert test_file.exists()
            
            # Get result triggers cleanup
            result = invoke_task.get_result()
            assert result == {"result": "data"}
            
            # Verify cleanup happened
            assert not temp_dir.exists()
            assert invoke_task._cleaned_up is True
            
            # Second cleanup should be no-op
            invoke_task._cleanup()  # Should not raise
            
    def test_cleanup_on_deletion(self):
        """Test cleanup happens on object deletion."""
        mock_task = Mock()
        
        with tempfile.TemporaryDirectory() as base_dir:
            temp_dir = Path(base_dir) / "flow-invoke-test"
            temp_dir.mkdir()
            
            invoke_task = InvokeTask(mock_task, Path("/tmp/result.json"), temp_dir)
            assert temp_dir.exists()
            
            # Delete object
            del invoke_task
            
            # Directory should be cleaned up
            assert not temp_dir.exists()


class TestInvokeFunction:
    """Integration tests for the invoke function."""
    
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_basic_success(self, mock_tempfile, mock_flow_class):
        """Test basic successful invocation."""
        # Create test module
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test_module.py"
            module_path.write_text("""
def add(a, b):
    return a + b
""")
            
            # Mock tempfile behavior
            result_file = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file = tempfile.NamedTemporaryFile(delete=False)
            
            files = [result_file, wrapper_file]
            mock_tempfile.side_effect = files
            
            # Write expected result
            with open(result_file.name, 'w') as f:
                json.dump(7, f)
            
            # Mock Flow and task
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "completed"
            mock_task.logs.return_value = "Success"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Test invocation
            result = invoke(str(module_path), "add", args=[3, 4], instance_type="cpu")
            
            assert result == 7
            
            # Verify Flow was called correctly
            mock_flow.run.assert_called_once()
            config = mock_flow.run.call_args[0][0]
            assert config.name == "invoke-add"
            assert "python" in config.command
            
            # Cleanup
            Path(result_file.name).unlink(missing_ok=True)
            Path(wrapper_file.name).unlink(missing_ok=True)
            
    def test_invoke_module_not_found(self):
        """Test error when module doesn't exist."""
        with pytest.raises(ValidationError) as exc:
            invoke("/nonexistent/module.py", "func")
        assert "Module not found" in str(exc.value)
        
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_with_kwargs(self, mock_tempfile, mock_flow_class):
        """Test invocation with keyword arguments."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("""
def process(data, scale=1.0, offset=0):
    return {"result": data * scale + offset}
""")
            
            # Mock setup
            result_file = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file = tempfile.NamedTemporaryFile(delete=False)
            mock_tempfile.side_effect = [result_file, wrapper_file]
            
            # Expected result
            expected = {"result": 25.0}
            with open(result_file.name, 'w') as f:
                json.dump(expected, f)
                
            # Mock Flow
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "completed"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Test
            result = invoke(
                str(module_path), 
                "process",
                args=[10],
                kwargs={"scale": 2.0, "offset": 5},
                instance_type="cpu"
            )
            
            assert result == expected
            
            # Cleanup
            Path(result_file.name).unlink(missing_ok=True)
            Path(wrapper_file.name).unlink(missing_ok=True)
            
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_task_params(self, mock_tempfile, mock_flow_class):
        """Test passing Flow task parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 42")
            
            # Mock setup
            result_file = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file = tempfile.NamedTemporaryFile(delete=False)
            mock_tempfile.side_effect = [result_file, wrapper_file]
            
            with open(result_file.name, 'w') as f:
                json.dump(42, f)
                
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "completed"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Test with various task parameters
            result = invoke(
                str(module_path),
                "func",
                gpu="a100",
                max_price_per_hour=25.0,
                num_instances=2,
                environment={"KEY": "value"},
                volumes={"/data": "volume-id"}
            )
            
            # Verify task config
            config = mock_flow.run.call_args[0][0]
            assert config.instance_type == "a100"
            assert config.max_price_per_hour == 25.0
            assert config.num_instances == 2
            assert config.environment == {"KEY": "value"}
            assert config.volumes == {"/data": "volume-id"}
            
            # Cleanup
            Path(result_file.name).unlink(missing_ok=True)
            Path(wrapper_file.name).unlink(missing_ok=True)


class TestInvokeAsync:
    """Tests for invoke_async function."""
    
    @patch('flow.api.invoke.Flow')
    def test_invoke_async_returns_task(self, mock_flow_class):
        """Test that invoke_async returns InvokeTask immediately."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 'async result'")
            
            # Mock Flow
            mock_flow = Mock()
            mock_task = Mock()
            mock_task.task_id = "async-123"
            mock_task.status = "pending"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value = mock_flow
            
            # Test async invocation
            invoke_task = invoke_async(str(module_path), "func", gpu="a100")
            
            # Should return InvokeTask immediately
            assert isinstance(invoke_task, InvokeTask)
            assert invoke_task.task == mock_task
            
            # Task should be submitted without wait
            mock_flow.run.assert_called_once()
            assert mock_flow.run.call_args[1]["wait"] is False
            
    @patch('flow.api.invoke.Flow')
    def test_invoke_async_cleanup_path(self, mock_flow_class):
        """Test that invoke_async creates unique temp directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): pass")
            
            mock_flow = Mock()
            mock_task = Mock()
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value = mock_flow
            
            # Create multiple async invocations
            tasks = []
            temp_dirs = set()
            
            for _ in range(3):
                task = invoke_async(str(module_path), "func", instance_type="cpu")
                tasks.append(task)
                temp_dirs.add(str(task._temp_dir))
                
            # Each should have unique temp directory
            assert len(temp_dirs) == 3
            
            # All should have flow-invoke prefix
            for temp_dir in temp_dirs:
                assert "flow-invoke-" in temp_dir