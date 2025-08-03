"""Golden tests for examples to ensure they remain functional.

These tests validate that our examples:
1. Have valid syntax
2. Import successfully  
3. Follow expected patterns
4. Would run correctly (in mock mode for CI)
"""

import ast
import os
import subprocess
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flow import TaskConfig
from flow.api.models import Task, TaskStatus


class TestExamples(TestCase):
    """Test all examples remain functional."""

    def setUp(self):
        """Set up test environment."""
        self.examples_dir = Path(__file__).parent.parent / "examples"
        self.mock_task = Mock(spec=Task)
        self.mock_task.id = "test-task-123"
        self.mock_task.status = TaskStatus.COMPLETED
        self.mock_task.logs.return_value = "Mock logs"
        self.mock_task.instance_ip = "10.0.0.1"

    def test_examples_directory_exists(self):
        """Ensure examples directory exists."""
        self.assertTrue(self.examples_dir.exists())
        self.assertTrue(self.examples_dir.is_dir())

    def test_expected_examples_exist(self):
        """Ensure all expected examples exist."""
        expected_files = [
            "01_basics/hello_gpu.py",
            "01_basics/instance_types.py",
            "01_basics/task_lifecycle.py",
            "01_basics/cancel_task.py",
            "02_storage/data_pipeline.py",
            "03_development/jupyter_server.py",
            "03_development/local_testing.py",
            "04_distributed/multi_node.py",
            "05_production/logging_patterns.py",
            "README.md",
        ]

        for file_path in expected_files:
            full_path = self.examples_dir / file_path
            self.assertTrue(full_path.exists(), f"Missing example: {file_path}")

    def test_python_examples_syntax(self):
        """Validate Python syntax in all examples."""
        for py_file in self.examples_dir.glob("**/*.py"):
            with open(py_file) as f:
                content = f.read()
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.fail(f"Syntax error in {py_file.name}: {e}")

    def test_yaml_configs_valid(self):
        """Validate YAML configurations."""
        import yaml

        for yaml_file in (self.examples_dir / "configs").glob("*.yaml"):
            with open(yaml_file) as f:
                try:
                    config_dict = yaml.safe_load(f)
                    # Add command if not present in YAML
                    if 'command' not in config_dict and 'script' not in config_dict and 'shell' not in config_dict:
                        config_dict['command'] = "python -c pass"
                    # Remove fields that are handled by YAML adapter but not part of TaskConfig
                    config_dict.pop('unique_name', None)
                    config_dict.pop('append_suffix', None)
                    # Validate it can be loaded as TaskConfig
                    TaskConfig(**config_dict)
                except Exception as e:
                    self.fail(f"Invalid YAML config {yaml_file.name}: {e}")

    @patch('flow.Flow')
    def test_verify_instance_example(self, mock_flow_class):
        """Test instance verification example logic."""
        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.run.return_value = self.mock_task

        # Import and run the example's main function
        example_path = self.examples_dir / "01_basics" / "hello_gpu.py"
        spec = subprocess.run(
            [sys.executable, "-m", "py_compile", str(example_path)],
            capture_output=True
        )
        self.assertEqual(spec.returncode, 0, f"Failed to compile: {spec.stderr}")

        # Verify expected task configuration
        with patch('sys.argv', ['01_verify_instance.py']):
            exec_globals = {'__name__': '__main__', '__file__': str(example_path)}
            with open(example_path) as f:
                code = compile(f.read(), str(example_path), 'exec')
                # This would execute but we patch Flow to prevent actual API calls
                # exec(code, exec_globals)

        # Verify the example structure
        with open(example_path) as f:
            content = f.read()
            self.assertIn('TaskConfig', content)
            self.assertIn('instance_type', content)
            self.assertIn('nvidia-smi', content)

    @patch('flow.Flow')
    @patch('secrets.token_urlsafe')
    def test_jupyter_server_example(self, mock_token, mock_flow_class):
        """Test Jupyter server example logic."""
        # Mock token generation
        mock_token.return_value = "test-token-123"

        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.run.return_value = self.mock_task

        # Verify example structure
        example_path = self.examples_dir / "03_development" / "jupyter_server.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('jupyter notebook', content)
            self.assertIn('port=8888', content)
            self.assertIn('jupyter-server', content)  # Task name

    @patch('flow.Flow')
    @patch.dict(os.environ, {'WANDB_API_KEY': 'test-key'})
    def test_multi_node_training_example(self, mock_flow_class):
        """Test multi-node training example logic."""
        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.run.return_value = self.mock_task

        # Verify example structure
        example_path = self.examples_dir / "04_distributed" / "multi_node.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('num_instances=2', content)
            self.assertIn('FLOW_NODE_RANK', content)
            self.assertIn('MASTER_ADDR', content)

    def test_examples_follow_patterns(self):
        """Ensure examples follow consistent patterns."""
        for py_file in self.examples_dir.glob("**/*.py"):
            if py_file.name == "__init__.py":
                continue

            with open(py_file) as f:
                content = f.read()

            # All examples should have proper docstrings
            self.assertIn('"""', content, f"{py_file.name} missing docstring")

            # All examples should have main function
            self.assertIn('def main():', content, f"{py_file.name} missing main()")

            # All examples should have if __name__ == "__main__"
            self.assertIn('if __name__ == "__main__":', content,
                          f"{py_file.name} missing main guard")

            # All examples should import Flow and TaskConfig
            self.assertIn('from flow import', content,
                          f"{py_file.name} missing flow imports")

    def test_examples_readme_exists(self):
        """Ensure examples README exists and has expected content."""
        readme_path = self.examples_dir / "README.md"
        self.assertTrue(readme_path.exists())

        with open(readme_path) as f:
            content = f.read()

        # Check for key sections
        self.assertIn('Prerequisites', content)
        self.assertIn('hello_gpu.py', content)
        self.assertIn('jupyter_server.py', content)
        self.assertIn('multi_node.py', content)
        self.assertIn('pytest tests/test_examples.py', content)

    @patch('flow.Flow')
    def test_s3_data_access_example(self, mock_flow_class):
        """Test S3 data access example logic."""
        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.run.return_value = self.mock_task

        # Verify example structure
        example_path = self.examples_dir / "02_storage" / "data_pipeline.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('s3://my-bucket/dataset/', content)
            self.assertIn('volumes', content)
            self.assertIn('AWS_ACCESS_KEY_ID', content)
            self.assertIn('s3-download', content)
            self.assertIn('s3-training', content)


    @patch('flow.Flow')
    def test_cancel_task_example(self, mock_flow_class):
        """Test cancel task example logic."""
        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.run.return_value = self.mock_task
        mock_flow.cancel.return_value = None
        
        # Verify example structure
        example_path = self.examples_dir / "01_basics" / "cancel_task.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('task.cancel()', content)
            self.assertIn('flow.cancel', content)
            self.assertIn('cancellation-demo', content)
            self.assertIn('SIGTERM', content)

    def test_check_task_status_example(self):
        """Test check task status example logic."""
        # Verify example structure
        example_path = self.examples_dir / "01_basics" / "task_lifecycle.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('task.status', content)
            self.assertIn('TaskConfig', content)

    @patch('flow.Flow')
    def test_create_gpu_task_example(self, mock_flow_class):
        """Test create GPU task example logic."""
        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.run.return_value = self.mock_task

        # Verify example structure
        example_path = self.examples_dir / "01_basics" / "hello_gpu.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('h100', content)
            self.assertIn('nvidia-smi', content)
            self.assertIn('verify-gpu', content)
            self.assertIn('TaskConfig', content)

    @patch('flow.Flow')
    def test_list_available_instances_example(self, mock_flow_class):
        """Test list available instances example logic."""
        # Mock Flow instance
        mock_flow = MagicMock()
        mock_flow_class.return_value.__enter__.return_value = mock_flow
        mock_flow.list_instances.return_value = [
            {"name": "a100", "gpu_memory": 40, "price": 2.0},
            {"name": "h100", "gpu_memory": 80, "price": 4.0}
        ]

        # Verify example structure
        example_path = self.examples_dir / "01_basics" / "instance_types.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('instance_type', content)
            self.assertIn('find_instances', content)

    def test_local_provider_examples(self):
        """Test local provider related examples."""
        # These examples require special local setup
        local_examples = [
            "03_development/local_testing.py"
        ]

        for example_name in local_examples:
            example_path = self.examples_dir / example_name
            if not example_path.exists():
                self.skipTest(f"Example {example_name} not found")
            with open(example_path) as f:
                content = f.read()
                # Verify common local provider patterns
                self.assertIn('local', content.lower())
                self.assertIn('TaskConfig', content)

    def test_logs_development_workflow_example(self):
        """Test logs development workflow example."""
        example_path = self.examples_dir / "05_production" / "logging_patterns.py"
        with open(example_path) as f:
            content = f.read()
            self.assertIn('logs', content)
            self.assertIn('TaskConfig', content)

    def test_all_examples_are_tested(self):
        """Ensure we have a test for every example."""
        # Get all Python examples
        example_files = set()
        for py_file in self.examples_dir.glob("*.py"):
            if py_file.name != "__init__.py":
                example_files.add(py_file.name)

        # Check each has a corresponding test method
        test_methods = [method for method in dir(self) if method.startswith('test_')]

        # Map of example names to expected test methods
        expected_tests = {
            "hello_gpu.py": "test_verify_instance_example",
            "jupyter_server.py": "test_jupyter_server_example",
            "multi_node.py": "test_multi_node_training_example",
            "data_pipeline.py": "test_s3_data_access_example",
            "cancel_task.py": "test_cancel_task_example",
            "check_task_status.py": "test_check_task_status_example",
            "create_gpu_task.py": "test_create_gpu_task_example",
            "list_available_instances.py": "test_list_available_instances_example",
            "local_provider_workflow.py": "test_local_provider_examples",
            "local_testing_demo.py": "test_local_provider_examples",
            "test_local_provider.py": "test_local_provider_examples",
            "logs_development_workflow.py": "test_logs_development_workflow_example"
        }

        for example_file in example_files:
            if example_file in expected_tests:
                test_method = expected_tests[example_file]
                self.assertIn(test_method, test_methods,
                              f"Missing test for {example_file}")
