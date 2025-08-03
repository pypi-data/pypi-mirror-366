"""Integration tests for invoke module.

Tests complex scenarios including concurrent execution, error handling,
and real-world usage patterns.
"""

import concurrent.futures
import json
import os
import tempfile
import time
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch, MagicMock

import pytest

from flow.api.invoke import invoke, invoke_async, InvokeTask
from flow.errors import TaskExecutionError, ValidationError


class TestInvokeIntegrationScenarios:
    """Integration tests for complex invoke scenarios."""
    
    @patch('flow.api.invoke.Flow')
    def test_concurrent_invoke_operations(self, mock_flow_class):
        """Test multiple concurrent invocations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test modules
            modules = []
            for i in range(5):
                module_path = Path(temp_dir) / f"module_{i}.py"
                module_path.write_text(f"""
def process(x):
    return x * {i + 1}
""")
                modules.append(module_path)
            
            # Mock Flow behavior
            def create_mock_flow():
                mock_flow = MagicMock()
                mock_task = Mock()
                mock_task.status = "completed"
                mock_flow.run.return_value = mock_task
                return mock_flow
                
            mock_flow_class.return_value.__enter__.side_effect = create_mock_flow
            
            # Prepare result files
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                result_files = []
                wrapper_files = []
                
                for i in range(5):
                    result_file = tempfile.NamedTemporaryFile(delete=False)
                    wrapper_file = tempfile.NamedTemporaryFile(delete=False)
                    result_files.append(result_file)
                    wrapper_files.append(wrapper_file)
                    
                    # Write expected result
                    with open(result_file.name, 'w') as f:
                        json.dump(10 * (i + 1), f)
                        
                # Configure mock to return files in order
                all_files = []
                for r, w in zip(result_files, wrapper_files):
                    all_files.extend([r, w])
                mock_tempfile.side_effect = all_files
                
                # Run concurrent invocations
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for i, module in enumerate(modules):
                        future = executor.submit(
                            invoke, 
                            str(module), 
                            "process", 
                            args=[10],
                            instance_type="cpu"
                        )
                        futures.append(future)
                    
                    # Collect results
                    results = [f.result() for f in futures]
                    
                # Verify results
                assert sorted(results) == [10, 20, 30, 40, 50]
                
                # Cleanup
                for f in result_files + wrapper_files:
                    Path(f.name).unlink(missing_ok=True)
                    
    @patch('flow.api.invoke.Flow')
    def test_large_result_handling(self, mock_flow_class):
        """Test handling results near the size limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "large_result.py"
            module_path.write_text("""
def generate_large_data(size_mb):
    # Generate data of approximately size_mb megabytes
    data = "x" * (size_mb * 1024 * 1024)
    return {"data": data, "size": len(data)}
""")
            
            # Test just under limit (9MB)
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                result_file = tempfile.NamedTemporaryFile(delete=False)
                wrapper_file = tempfile.NamedTemporaryFile(delete=False)
                mock_tempfile.side_effect = [result_file, wrapper_file]
                
                # Create 9MB result
                large_data = "x" * (9 * 1024 * 1024)
                result_data = {"data": large_data, "size": len(large_data)}
                with open(result_file.name, 'w') as f:
                    json.dump(result_data, f)
                    
                # Mock Flow
                mock_flow = MagicMock()
                mock_task = Mock()
                mock_task.status = "completed"
                mock_flow.run.return_value = mock_task
                mock_flow_class.return_value.__enter__.return_value = mock_flow
                
                # Should succeed
                result = invoke(str(module_path), "generate_large_data", args=[9], instance_type="cpu")
                assert result["size"] == 9 * 1024 * 1024
                
                # Cleanup
                Path(result_file.name).unlink(missing_ok=True)
                Path(wrapper_file.name).unlink(missing_ok=True)
                
    @patch('flow.api.invoke.Flow')
    def test_module_import_failure(self, mock_flow_class):
        """Test handling of module import failures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create module with import error
            module_path = Path(temp_dir) / "bad_import.py"
            module_path.write_text("""
import nonexistent_module  # This will fail

def process():
    return "never reached"
""")
            
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                result_file = tempfile.NamedTemporaryFile(delete=False)
                wrapper_file = tempfile.NamedTemporaryFile(delete=False)
                mock_tempfile.side_effect = [result_file, wrapper_file]
                
                # Mock Flow with failed task
                mock_flow = MagicMock()
                mock_task = Mock()
                mock_task.status = "failed"
                mock_task.logs.return_value = """
Loading function 'process' from /tmp/bad_import.py
ERROR: Function execution failed: ModuleNotFoundError: No module named 'nonexistent_module'
Traceback (most recent call last):
  File "<string>", line 20, in <module>
ModuleNotFoundError: No module named 'nonexistent_module'
"""
                mock_flow.run.return_value = mock_task
                mock_flow_class.return_value.__enter__.return_value = mock_flow
                
                # Should raise error
                with pytest.raises(RuntimeError) as exc:
                    invoke(str(module_path), "process", instance_type="cpu")
                assert "Task failed with status failed" in str(exc.value)
                
                # Cleanup
                Path(result_file.name).unlink(missing_ok=True)
                Path(wrapper_file.name).unlink(missing_ok=True)
                
    @patch('flow.api.invoke.Flow')
    def test_function_not_found(self, mock_flow_class):
        """Test handling when function doesn't exist in module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "module.py"
            module_path.write_text("""
def existing_function():
    return "exists"
""")
            
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                result_file = tempfile.NamedTemporaryFile(delete=False)
                wrapper_file = tempfile.NamedTemporaryFile(delete=False)
                mock_tempfile.side_effect = [result_file, wrapper_file]
                
                # Mock Flow with error logs
                mock_flow = MagicMock()
                mock_task = Mock()
                mock_task.status = "failed"
                mock_task.logs.return_value = """
Loading function 'nonexistent' from module.py
ERROR: Function 'nonexistent' not found in module
"""
                mock_flow.run.return_value = mock_task
                mock_flow_class.return_value.__enter__.return_value = mock_flow
                
                with pytest.raises(RuntimeError) as exc:
                    invoke(str(module_path), "nonexistent", instance_type="cpu")
                assert "Function 'nonexistent' not found" in str(exc.value)
                
                # Cleanup
                Path(result_file.name).unlink(missing_ok=True)
                Path(wrapper_file.name).unlink(missing_ok=True)
                
    @patch('flow.api.invoke.Flow')
    def test_error_propagation(self, mock_flow_class):
        """Test that errors in remote functions are properly propagated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "error_module.py"
            module_path.write_text("""
def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero!")
    return a / b
    
def process_data(data):
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data).__name__}")
    return sum(data)
""")
            
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                result_file = tempfile.NamedTemporaryFile(delete=False)
                wrapper_file = tempfile.NamedTemporaryFile(delete=False)
                mock_tempfile.side_effect = [result_file, wrapper_file]
                
                # Mock Flow with error
                mock_flow = MagicMock()
                mock_task = Mock()
                mock_task.status = "failed"
                mock_task.logs.return_value = """
Executing divide...
ERROR: Function execution failed: ValueError: Division by zero!
Traceback (most recent call last):
  File "<string>", line 236, in <module>
  File "error_module.py", line 4, in divide
    raise ValueError("Division by zero!")
ValueError: Division by zero!
"""
                mock_flow.run.return_value = mock_task
                mock_flow_class.return_value.__enter__.return_value = mock_flow
                
                with pytest.raises(RuntimeError) as exc:
                    invoke(str(module_path), "divide", args=[10, 0], instance_type="cpu")
                assert "Division by zero!" in str(exc.value)
                
                # Cleanup
                Path(result_file.name).unlink(missing_ok=True)
                Path(wrapper_file.name).unlink(missing_ok=True)
                
    def test_cleanup_on_failure(self):
        """Test that temporary files are cleaned up on various failures."""
        # Track created temp files
        created_files = []
        
        original_tempfile = tempfile.NamedTemporaryFile
        
        def tracking_tempfile(*args, **kwargs):
            f = original_tempfile(*args, **kwargs)
            created_files.append(f.name)
            return f
            
        with patch('tempfile.NamedTemporaryFile', tracking_tempfile):
            # Test with non-existent module
            with pytest.raises(ValidationError):
                invoke("/nonexistent/module.py", "func")
                
            # No temp files should be created for validation error
            assert len(created_files) == 0
            
            # Test with existing module but task failure
            with tempfile.TemporaryDirectory() as temp_dir:
                module_path = Path(temp_dir) / "test.py"
                module_path.write_text("def func(): return 42")
                
                with patch('flow.api.invoke.Flow') as mock_flow_class:
                    mock_flow = MagicMock()
                    mock_task = Mock()
                    mock_task.status = "failed"
                    mock_task.logs.return_value = "ERROR: Some error"
                    mock_flow.run.return_value = mock_task
                    mock_flow_class.return_value.__enter__.return_value = mock_flow
                    
                    with pytest.raises(RuntimeError):
                        invoke(str(module_path), "func", instance_type="cpu", retries=0)
                        
                    # Files should be created
                    assert len(created_files) == 2  # result and wrapper
                    
                    # With the retry logic, cleanup happens on successful returns
                    # or after all retries are exhausted. Check that at least 
                    # the wrapper file is cleaned up (result file may not exist)
                    wrapper_files = [f for f in created_files if f.endswith('.py')]
                    for f in wrapper_files:
                        assert not Path(f).exists()


class TestInvokeAsyncIntegration:
    """Integration tests for async invoke operations."""
    
    @patch('flow.api.invoke.Flow')
    def test_async_result_retrieval(self, mock_flow_class):
        """Test async execution and result retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "async_test.py"
            module_path.write_text("""
import time

def long_running_task(duration, result):
    time.sleep(duration)
    return {"completed": True, "result": result}
""")
            
            # Create a proper temp directory for async
            async_temp_dir = Path(temp_dir) / "flow-invoke-test"
            async_temp_dir.mkdir()
            result_path = async_temp_dir / "result.json"
            
            # Mock Flow
            mock_flow = Mock()
            mock_task = Mock()
            mock_task.task_id = "async-task-123"
            mock_task.status = "running"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value = mock_flow
            
            # Start async task
            with patch('tempfile.gettempdir', return_value=temp_dir):
                with patch('uuid.uuid4', return_value=Mock(hex="test1234")):
                    invoke_task = invoke_async(
                        str(module_path), 
                        "long_running_task",
                        args=[0.1, "async_result"],
                        instance_type="cpu"
                    )
            
            # Verify task started
            assert isinstance(invoke_task, InvokeTask)
            assert invoke_task.task == mock_task
            
            # Simulate task completion
            mock_task.status = "completed"
            expected_result = {"completed": True, "result": "async_result"}
            
            # Write result to the expected location
            result_path = invoke_task._result_path
            result_path.parent.mkdir(exist_ok=True)
            with open(result_path, 'w') as f:
                json.dump(expected_result, f)
            
            # Get result
            result = invoke_task.get_result()
            assert result == expected_result
            
            # Verify cleanup happened
            assert not invoke_task._temp_dir.exists()
            
    @patch('flow.api.invoke.Flow')
    def test_multiple_async_tasks(self, mock_flow_class):
        """Test managing multiple async tasks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test module
            module_path = Path(temp_dir) / "multi_async.py"
            module_path.write_text("""
def process_batch(batch_id, items):
    return {
        "batch_id": batch_id,
        "processed": len(items),
        "sum": sum(items)
    }
""")
            
            # Mock Flow to return different tasks
            tasks = []
            
            def create_task(task_id):
                task = Mock()
                task.task_id = task_id
                task.status = "running"
                tasks.append(task)
                return task
                
            mock_flow = Mock()
            mock_flow.run.side_effect = [
                create_task("task-1"),
                create_task("task-2"),
                create_task("task-3")
            ]
            mock_flow_class.return_value = mock_flow
            
            # Submit multiple async tasks
            invoke_tasks = []
            
            with patch('tempfile.gettempdir', return_value=temp_dir):
                with patch('uuid.uuid4') as mock_uuid:
                    # Create mock UUIDs that return unique strings when str() is called
                    class MockUUID:
                        def __init__(self, value):
                            self.value = value
                        def __str__(self):
                            return self.value
                    
                    # Set up unique UUIDs for each call - only first 8 chars are used
                    mock_uuid.side_effect = [
                        MockUUID(f'{i}2345678-9000-0000-0000-000000000000')
                        for i in range(3)
                    ]
                    
                    for i in range(3):
                        invoke_task = invoke_async(
                            str(module_path),
                            "process_batch",
                            args=[i, list(range(i * 10, (i + 1) * 10))],
                            instance_type="cpu"
                        )
                        invoke_tasks.append(invoke_task)
            
            # Verify all tasks are independent
            assert len(set(t.task.task_id for t in invoke_tasks)) == 3
            # Check that temp directories are unique
            temp_dirs_list = [str(t._temp_dir) for t in invoke_tasks]
            assert len(set(temp_dirs_list)) == 3
            
            # Simulate completion and verify results
            for i, (invoke_task, mock_task) in enumerate(zip(invoke_tasks, tasks)):
                mock_task.status = "completed"
                
                # Write result
                result_data = {
                    "batch_id": i,
                    "processed": 10,
                    "sum": sum(range(i * 10, (i + 1) * 10))
                }
                with open(invoke_task._result_path, 'w') as f:
                    json.dump(result_data, f)
                
                # Get result
                result = invoke_task.get_result()
                assert result["batch_id"] == i
                assert result["processed"] == 10


class TestInvokeRealWorldScenarios:
    """Test real-world usage patterns."""
    
    @patch('flow.api.invoke.Flow')
    def test_ml_training_pattern(self, mock_flow_class):
        """Test ML training workflow pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create ML training module
            train_module = Path(temp_dir) / "train_model.py"
            train_module.write_text("""
def train_model(config_path, output_dir):
    import json
    
    # Load config
    with open(config_path) as f:
        config = json.load(f)
    
    # Simulate training
    metrics = {
        "epochs": config["epochs"],
        "final_loss": 0.05,
        "final_accuracy": 0.95,
        "model_path": f"{output_dir}/model.pt"
    }
    
    # Save metrics
    with open(f"{output_dir}/metrics.json", "w") as f:
        json.dump(metrics, f)
    
    return metrics
""")
            
            # Create config
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps({
                "epochs": 10,
                "learning_rate": 0.001,
                "batch_size": 32
            }))
            
            output_dir = Path(temp_dir) / "output"
            output_dir.mkdir()
            
            # Mock successful execution
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                result_file = tempfile.NamedTemporaryFile(delete=False)
                wrapper_file = tempfile.NamedTemporaryFile(delete=False)
                mock_tempfile.side_effect = [result_file, wrapper_file]
                
                expected_metrics = {
                    "epochs": 10,
                    "final_loss": 0.05,
                    "final_accuracy": 0.95,
                    "model_path": f"{output_dir}/model.pt"
                }
                
                with open(result_file.name, 'w') as f:
                    json.dump(expected_metrics, f)
                
                mock_flow = MagicMock()
                mock_task = Mock()
                mock_task.status = "completed"
                mock_flow.run.return_value = mock_task
                mock_flow_class.return_value.__enter__.return_value = mock_flow
                
                # Run training
                metrics = invoke(
                    str(train_module),
                    "train_model",
                    args=[str(config_path), str(output_dir)],
                    gpu="a100",
                    max_price_per_hour=25.0
                )
                
                assert metrics["final_accuracy"] == 0.95
                assert metrics["epochs"] == 10
                
                # Cleanup
                Path(result_file.name).unlink(missing_ok=True)
                Path(wrapper_file.name).unlink(missing_ok=True)
                
    @patch('flow.api.invoke.Flow')
    def test_data_pipeline_pattern(self, mock_flow_class):
        """Test data processing pipeline pattern."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create data processing modules
            preprocess_module = Path(temp_dir) / "preprocess.py"
            preprocess_module.write_text("""
def clean_data(input_path, output_path):
    # Simulate data cleaning
    return {
        "input_records": 1000,
        "output_records": 950,
        "removed": 50,
        "output_path": output_path
    }
""")
            
            transform_module = Path(temp_dir) / "transform.py"
            transform_module.write_text("""
def transform_data(input_path, output_path, format="parquet"):
    # Simulate transformation
    return {
        "transformed_records": 950,
        "output_format": format,
        "output_path": output_path
    }
""")
            
            # Mock Flow
            mock_flow = MagicMock()
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Track pipeline stages
            with patch('tempfile.NamedTemporaryFile') as mock_tempfile:
                # Stage 1: Preprocess
                result1 = tempfile.NamedTemporaryFile(delete=False)
                wrapper1 = tempfile.NamedTemporaryFile(delete=False)
                
                # Stage 2: Transform
                result2 = tempfile.NamedTemporaryFile(delete=False)
                wrapper2 = tempfile.NamedTemporaryFile(delete=False)
                
                mock_tempfile.side_effect = [result1, wrapper1, result2, wrapper2]
                
                # Set up stage 1 result
                stage1_result = {
                    "input_records": 1000,
                    "output_records": 950,
                    "removed": 50,
                    "output_path": "/tmp/cleaned.csv"
                }
                with open(result1.name, 'w') as f:
                    json.dump(stage1_result, f)
                
                # Set up stage 2 result
                stage2_result = {
                    "transformed_records": 950,
                    "output_format": "parquet",
                    "output_path": "/tmp/final.parquet"
                }
                with open(result2.name, 'w') as f:
                    json.dump(stage2_result, f)
                
                # Mock successful tasks
                mock_task = Mock()
                mock_task.status = "completed"
                mock_flow.run.return_value = mock_task
                
                # Run pipeline
                # Stage 1: Clean data
                clean_result = invoke(
                    str(preprocess_module),
                    "clean_data",
                    args=["/data/raw.csv", "/tmp/cleaned.csv"],
                    instance_type="cpu"
                )
                
                assert clean_result["removed"] == 50
                
                # Stage 2: Transform data
                transform_result = invoke(
                    str(transform_module),
                    "transform_data",
                    args=[clean_result["output_path"], "/tmp/final.parquet"],
                    kwargs={"format": "parquet"},
                    instance_type="cpu"
                )
                
                assert transform_result["output_format"] == "parquet"
                assert transform_result["transformed_records"] == 950
                
                # Cleanup
                for f in [result1, wrapper1, result2, wrapper2]:
                    Path(f.name).unlink(missing_ok=True)