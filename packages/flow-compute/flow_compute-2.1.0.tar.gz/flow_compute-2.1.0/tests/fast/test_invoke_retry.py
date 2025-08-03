"""Test retry logic for invoke function."""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from flow.api.invoke import invoke


class TestInvokeRetryLogic:
    """Test retry functionality in invoke."""
    
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_retry_on_task_failure(self, mock_tempfile, mock_flow_class):
        """Test that invoke retries on task failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 42")
            
            # Mock tempfile - create actual temp files
            result_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
            result_file.close()  # Close it so it can be opened by the code
            wrapper_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
            wrapper_file.close()
            
            # Mock to return these files
            def mock_temp(*args, **kwargs):
                if kwargs.get('suffix') == '.json':
                    f = type('obj', (object,), {'name': result_file.name})
                    return f
                else:
                    f = type('obj', (object,), {'name': wrapper_file.name})
                    return f
                    
            mock_tempfile.side_effect = mock_temp
            
            # Mock Flow with failures then success
            mock_flow = MagicMock()
            mock_task_fail1 = Mock()
            mock_task_fail1.status = "failed"
            mock_task_fail1.logs.return_value = "ERROR: Temporary failure"
            
            mock_task_fail2 = Mock()
            mock_task_fail2.status = "failed"
            mock_task_fail2.logs.return_value = "ERROR: Another temporary failure"
            
            mock_task_success = Mock()
            mock_task_success.status = "completed"
            
            # Set up sequential returns
            mock_flow.run.side_effect = [
                mock_task_fail1,
                mock_task_fail2,
                mock_task_success
            ]
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Write result for successful attempt
            with open(result_file.name, 'w') as f:
                json.dump(42, f)
            
            # Test with retries - should succeed on 3rd attempt
            start_time = time.time()
            result = invoke(
                str(module_path), 
                "func",
                instance_type="cpu",
                retries=2,
                retry_delay=0.1,
                retry_backoff=2.0
            )
            elapsed = time.time() - start_time
            
            assert result == 42
            assert mock_flow.run.call_count == 3
            # Should have delays: 0.1s after first failure, 0.2s after second
            assert elapsed >= 0.3
            
            # Cleanup
            Path(result_file.name).unlink(missing_ok=True)
            Path(wrapper_file.name).unlink(missing_ok=True)
            
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_retry_exhaustion(self, mock_tempfile, mock_flow_class):
        """Test that invoke raises after all retries are exhausted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 42")
            
            # Mock tempfile
            result_file = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file = tempfile.NamedTemporaryFile(delete=False)
            mock_tempfile.side_effect = [result_file, wrapper_file] * 3
            
            # Mock Flow with continuous failures
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "failed"
            mock_task.logs.return_value = "ERROR: Persistent failure"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Test with retries - should fail after all attempts
            with pytest.raises(RuntimeError) as exc:
                invoke(
                    str(module_path),
                    "func", 
                    instance_type="cpu",
                    retries=2,
                    retry_delay=0.05
                )
            
            assert "Task failed with status failed" in str(exc.value)
            assert "Persistent failure" in str(exc.value)
            assert mock_flow.run.call_count == 3  # Initial + 2 retries
            
            # Cleanup
            Path(result_file.name).unlink(missing_ok=True)
            Path(wrapper_file.name).unlink(missing_ok=True)
            
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_no_retry_on_success(self, mock_tempfile, mock_flow_class):
        """Test that successful invocation doesn't retry."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 'success'")
            
            # Mock tempfile
            result_file = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file = tempfile.NamedTemporaryFile(delete=False)
            mock_tempfile.side_effect = [result_file, wrapper_file]
            
            # Mock successful Flow
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "completed"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Write result
            with open(result_file.name, 'w') as f:
                json.dump("success", f)
            
            # Test with retries configured - should succeed immediately
            result = invoke(
                str(module_path),
                "func",
                instance_type="cpu",
                retries=3,
                retry_delay=1.0
            )
            
            assert result == "success"
            assert mock_flow.run.call_count == 1  # No retries needed
            
            # Cleanup
            Path(result_file.name).unlink(missing_ok=True)
            Path(wrapper_file.name).unlink(missing_ok=True)
            
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_retry_on_result_parse_error(self, mock_tempfile, mock_flow_class):
        """Test retry when result JSON is corrupted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 42")
            
            # Mock tempfile
            result_file1 = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file1 = tempfile.NamedTemporaryFile(delete=False)
            result_file2 = tempfile.NamedTemporaryFile(delete=False)
            wrapper_file2 = tempfile.NamedTemporaryFile(delete=False)
            mock_tempfile.side_effect = [
                result_file1, wrapper_file1,
                result_file2, wrapper_file2
            ]
            
            # Mock successful Flow
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "completed"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # First attempt: corrupted JSON
            with open(result_file1.name, 'w') as f:
                f.write("not valid json")
                
            # Second attempt: valid JSON
            with open(result_file2.name, 'w') as f:
                json.dump(42, f)
            
            # Test with retry - should succeed on second attempt
            result = invoke(
                str(module_path),
                "func",
                instance_type="cpu",
                retries=1,
                retry_delay=0.1
            )
            
            assert result == 42
            assert mock_flow.run.call_count == 2
            
            # Cleanup
            for f in [result_file1, wrapper_file1, result_file2, wrapper_file2]:
                Path(f.name).unlink(missing_ok=True)
                
    @patch('flow.api.invoke.Flow')
    @patch('tempfile.NamedTemporaryFile')
    def test_invoke_exponential_backoff(self, mock_tempfile, mock_flow_class):
        """Test exponential backoff timing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "test.py"
            module_path.write_text("def func(): return 42")
            
            # Mock tempfile - need enough for all attempts
            files = []
            for _ in range(8):  # 4 attempts * 2 files each
                files.append(tempfile.NamedTemporaryFile(delete=False))
            mock_tempfile.side_effect = files
            
            # Mock Flow with failures
            mock_flow = MagicMock()
            mock_task = Mock()
            mock_task.status = "failed"
            mock_task.logs.return_value = "ERROR: Failure"
            mock_flow.run.return_value = mock_task
            mock_flow_class.return_value.__enter__.return_value = mock_flow
            
            # Track timing
            start_time = time.time()
            
            with pytest.raises(RuntimeError):
                invoke(
                    str(module_path),
                    "func",
                    instance_type="cpu",
                    retries=3,
                    retry_delay=0.1,
                    retry_backoff=2.0
                )
            
            elapsed = time.time() - start_time
            
            # Expected delays: 0.1, 0.2, 0.4 = 0.7 seconds total
            assert elapsed >= 0.7
            assert elapsed < 1.0  # Should not be too much longer
            
            # Cleanup
            for f in files:
                Path(f.name).unlink(missing_ok=True)