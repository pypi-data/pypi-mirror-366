"""Integration tests for upload_code with LocalProvider.

These tests actually run code through the LocalProvider to verify
the complete upload_code pipeline works end-to-end.
"""

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Union

import pytest

from flow import Flow
from flow.api.models import TaskConfig


@contextmanager
def temp_project(files: Dict[str, Union[str, bytes]]):
    """Create a temporary project directory with given files.
    
    Context manager that creates a temporary directory, populates it with
    the specified files, changes to that directory, and cleans up afterwards.
    
    Args:
        files: Dictionary mapping file paths to their contents.
               Contents can be strings (text files) or bytes (binary files).
               
    Yields:
        str: Path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            for path, content in files.items():
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, bytes):
                    Path(path).write_bytes(content)
                else:
                    Path(path).write_text(content)
            yield tmpdir
        finally:
            os.chdir(old_cwd)


@pytest.mark.integration
class TestUploadCodeIntegration:
    """Integration tests that actually run code via LocalProvider.
    
    These tests verify the complete upload_code pipeline by running
    actual Docker containers with the LocalProvider. They ensure that
    code packaging, transfer, extraction, and execution all work together.
    
    Note:
        Tests are skipped if Docker is not available on the system.
    """

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_basic_upload_and_execution(self):
        """Test that uploaded code actually executes.
        
        Verifies that a simple Python script is correctly packaged,
        uploaded, extracted, and executed on the remote instance.
        """
        with temp_project({"hello.py": "print('Hello from uploaded code!')"}) as project_dir:
            # Use actual Flow with local provider
            flow = Flow()

            # Configure for local execution
            config = TaskConfig(
                name="test-upload",
                instance_type="local",
                command=["python", "hello.py"],
                upload_code=True,
                image="python:3.11-slim"  # Simple Python image
            )

            # Run the task
            task = flow.run(config)
            task.wait(timeout=30)

            # Check results
            logs = task.logs()
            assert "Hello from uploaded code!" in logs
            assert task.status == "completed"

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_directory_structure_preserved(self):
        """Test that directory structure is maintained."""
        with temp_project({
            "app/main.py": "from lib.utils import greet; greet()",
            "app/lib/__init__.py": "",
            "app/lib/utils.py": "def greet(): print('Structured project works!')"
        }) as project_dir:
            flow = Flow()

            config = TaskConfig(
                name="test-structure",
                instance_type="local",
                command=["python", "app/main.py"],
                upload_code=True,
                image="python:3.11-slim"
            )

            task = flow.run(config)
            task.wait(timeout=30)

            logs = task.logs()
            assert "Structured project works!" in logs
            assert task.status == "completed"

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_working_directory_behavior(self):
        """Test that working directory is set correctly."""
        with temp_project({
            "check_env.py": """
import os
print(f"CWD: {os.getcwd()}")
print(f"Files: {sorted(os.listdir())}")
print(f"Python file exists: {os.path.exists('check_env.py')}")
"""
        }) as project_dir:
            flow = Flow()

            config = TaskConfig(
                name="test-cwd",
                instance_type="local",
                command=["python", "check_env.py"],
                upload_code=True,
                image="python:3.11-slim"
            )

            task = flow.run(config)
            task.wait(timeout=30)

            logs = task.logs()
            assert "CWD: /workspace" in logs
            assert "check_env.py" in logs
            assert "Python file exists: True" in logs

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_flowignore_functionality(self):
        """Test that .flowignore excludes files correctly."""
        with temp_project({
            ".flowignore": "*.log\n__pycache__/\ntemp/",
            "list_files.py": """
import os
for root, dirs, files in os.walk('.'):
    for f in sorted(files):
        print(os.path.join(root, f))
""",
            "keep_me.py": "# This should be uploaded",
            "exclude_me.log": "# This should NOT be uploaded",
            "temp/data.txt": "# This should NOT be uploaded",
            "__pycache__/cache.pyc": b"# This should NOT be uploaded"
        }) as project_dir:
            flow = Flow()

            config = TaskConfig(
                name="test-flowignore",
                instance_type="local",
                command=["python", "list_files.py"],
                upload_code=True,
                image="python:3.11-slim"
            )

            task = flow.run(config)
            task.wait(timeout=30)

            logs = task.logs()
            assert "keep_me.py" in logs
            assert "list_files.py" in logs
            assert ".flowignore" in logs  # .flowignore itself is uploaded
            assert "exclude_me.log" not in logs
            assert "temp/data.txt" not in logs
            assert "__pycache__" not in logs

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_upload_code_false(self):
        """Test that upload_code=False doesn't upload files."""
        with temp_project({"should_not_exist.py": "print('This should not run')"}) as project_dir:
            flow = Flow()

            config = TaskConfig(
                name="test-no-upload",
                instance_type="local",
                command=["python", "should_not_exist.py"],
                upload_code=False,  # Explicitly disable upload
                image="python:3.11-slim"
            )

            task = flow.run(config)
            task.wait(timeout=30)

            # Should fail because file doesn't exist
            assert task.status == "failed"
            logs = task.logs()
            assert "No such file or directory" in logs or "can't open file" in logs

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_requirements_installation(self):
        """Test installing dependencies from requirements.txt."""
        with temp_project({
            "requirements.txt": "requests==2.31.0",
            "test_deps.py": """
import requests
print(f"Requests version: {requests.__version__}")
response = requests.get('https://httpbin.org/json')
print(f"Status: {response.status_code}")
"""
        }) as project_dir:
            flow = Flow()

            config = TaskConfig(
                name="test-requirements",
                instance_type="local",
                # Install deps then run
                command=["sh", "-c", "pip install -r requirements.txt && python test_deps.py"],
                upload_code=True,
                image="python:3.11-slim"
            )

            task = flow.run(config)
            task.wait(timeout=60)  # Longer timeout for pip install

            logs = task.logs()
            assert "Requests version: 2.31.0" in logs
            assert "Status: 200" in logs
            assert task.status == "completed"

    @pytest.mark.skipif(
        not os.path.exists('/var/run/docker.sock'),
        reason="Docker not available"
    )
    def test_complex_ml_workflow(self):
        """Test a realistic ML workflow with config and data files."""
        with temp_project({
            "train.py": """
import json
import os

print("Starting training...")

# Load config
with open('config.json') as f:
    config = json.load(f)
    print(f"Config loaded: {config}")

# Check data exists
assert os.path.exists('data/train.csv'), "Training data not found"
print("Training data found")

# Simulate training
print(f"Training for {config['epochs']} epochs...")
print(f"Learning rate: {config['lr']}")

# Save results
os.makedirs('outputs', exist_ok=True)
with open('outputs/metrics.json', 'w') as f:
    json.dump({'final_loss': 0.023, 'accuracy': 0.97}, f)

print("Training completed successfully!")
""",
            "config.json": '{"epochs": 10, "lr": 0.001}',
            "data/train.csv": "feature1,feature2,label\n1.0,2.0,0\n3.0,4.0,1"
        }) as project_dir:
            flow = Flow()

            config = TaskConfig(
                name="test-ml-workflow",
                instance_type="local",
                command=["python", "train.py"],
                upload_code=True,
                image="python:3.11-slim"
            )

            task = flow.run(config)
            task.wait(timeout=30)

            logs = task.logs()
            assert "Starting training..." in logs
            assert "Config loaded:" in logs
            assert "Training data found" in logs
            assert "Training for 10 epochs..." in logs
            assert "Learning rate: 0.001" in logs
            assert "Training completed successfully!" in logs
            assert task.status == "completed"
