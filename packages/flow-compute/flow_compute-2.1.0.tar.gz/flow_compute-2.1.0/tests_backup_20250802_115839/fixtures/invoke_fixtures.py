"""Test fixtures for invoke functionality.

Following Knuth's principle: Programs are meant to be read by humans.
Make test intent clear, hide complexity.
"""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from flow.api.models import Task


class InvokeTestContext:
    """Context manager for invoke tests that handles all mocking cleanly.
    
    This follows the principle of making the common case easy and correct.
    """

    def __init__(self):
        self.result_data = None
        self.should_fail = False
        self.error_message = None
        self.temp_files = []

    def with_result(self, data: Any) -> 'InvokeTestContext':
        """Set the expected result data."""
        self.result_data = data
        return self

    def with_error(self, error_msg: str) -> 'InvokeTestContext':
        """Configure to simulate an error."""
        self.should_fail = True
        self.error_message = error_msg
        return self

    def __enter__(self):
        """Set up all mocks in a consistent way."""
        # Patch tempfile to control result file creation
        self.tempfile_patch = patch('tempfile.NamedTemporaryFile')
        mock_tempfile = self.tempfile_patch.start()

        original_tempfile = tempfile.NamedTemporaryFile

        def controlled_tempfile(*args, **kwargs):
            if kwargs.get('suffix') == '.json':
                # Result file
                f = original_tempfile(*args, **kwargs)
                self.temp_files.append(f.name)

                if not self.should_fail and self.result_data is not None:
                    # Write result data
                    with open(f.name, 'w') as rf:
                        json.dump(self.result_data, rf)
                elif self.should_fail:
                    # Delete file to simulate missing result
                    Path(f.name).unlink(missing_ok=True)

                return f
            else:
                # Wrapper script
                return original_tempfile(*args, **kwargs)

        mock_tempfile.side_effect = controlled_tempfile

        # Create flow mock
        self.flow_patch = patch('flow.invoke.Flow')
        mock_flow_class = self.flow_patch.start()

        self.mock_flow = Mock()
        self.mock_task = self._create_task()

        self.mock_flow.run.return_value = self.mock_task
        mock_flow_class.return_value.__enter__.return_value = self.mock_flow

        return self

    def __exit__(self, *args):
        """Clean up all resources."""
        self.tempfile_patch.stop()
        self.flow_patch.stop()

        # Clean up temp files
        for f in self.temp_files:
            Path(f).unlink(missing_ok=True)

    def _create_task(self) -> Mock:
        """Create a mock task with proper behavior."""
        task = Mock(spec=Task)
        task.task_id = "test-task-123"
        task.status = "completed"

        if self.should_fail and self.error_message:
            task.logs.return_value = f"ERROR: {self.error_message}"
        else:
            task.logs.return_value = "Task completed successfully"

        return task


def create_test_module(content: str) -> str:
    """Create a temporary Python module for testing.
    
    Returns path to the created file.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(content)
        return f.name


def cleanup_test_module(path: str):
    """Clean up test module."""
    Path(path).unlink(missing_ok=True)
