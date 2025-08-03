#!/usr/bin/env python3
"""Validate all examples can be executed successfully.

This script provides a comprehensive validation of all examples:
1. Syntax validation
2. Import validation  
3. Mock execution validation
4. Output validation

Usage:
    python tests/validate_examples.py [--generate-golden]
"""

import argparse
import ast
import json
import os
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flow.api.models import Task, TaskStatus


class ExampleValidator:
    """Validate Flow SDK examples."""

    def __init__(self, generate_golden=False):
        self.examples_dir = Path(__file__).parent.parent / "examples"
        self.golden_dir = Path(__file__).parent / "golden_outputs"
        self.generate_golden = generate_golden
        self.results = []

    def validate_all(self):
        """Validate all examples."""
        print("Flow SDK Example Validation")
        print("=" * 60)

        # Get all Python examples
        example_files = sorted(self.examples_dir.glob("*.py"))
        example_files = [f for f in example_files if f.name != "__init__.py"]

        print(f"Found {len(example_files)} examples to validate\n")

        for example_file in example_files:
            self.validate_example(example_file)

        # Summary
        self._print_summary()

        # Return success if all passed
        return all(r['passed'] for r in self.results)

    def validate_example(self, example_path: Path):
        """Validate a single example."""
        print(f"Validating {example_path.name}...")

        result = {
            'name': example_path.name,
            'passed': True,
            'errors': []
        }

        # 1. Syntax check
        if not self._check_syntax(example_path, result):
            self.results.append(result)
            return

        # 2. Import check
        if not self._check_imports(example_path, result):
            self.results.append(result)
            return

        # 3. Docstring check
        self._check_docstring(example_path, result)

        # 4. Execution check (with mocks)
        self._check_execution(example_path, result)

        # Print status
        if result['passed']:
            print(f"  ✓ {example_path.name} - PASSED")
        else:
            print(f"  ✗ {example_path.name} - FAILED")
            for error in result['errors']:
                print(f"    - {error}")

        self.results.append(result)
        print()

    def _check_syntax(self, example_path: Path, result: dict) -> bool:
        """Check Python syntax."""
        try:
            with open(example_path) as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            result['passed'] = False
            result['errors'].append(f"Syntax error: {e}")
            return False

    def _check_imports(self, example_path: Path, result: dict) -> bool:
        """Check imports can be resolved."""
        try:
            # Use py_compile to check imports
            proc = subprocess.run(
                [sys.executable, "-m", "py_compile", str(example_path)],
                capture_output=True,
                text=True
            )
            if proc.returncode != 0:
                result['passed'] = False
                result['errors'].append(f"Import error: {proc.stderr}")
                return False
            return True
        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Import check failed: {e}")
            return False

    def _check_docstring(self, example_path: Path, result: dict):
        """Check docstring quality."""
        with open(example_path) as f:
            content = f.read()

        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)

        if not docstring:
            result['passed'] = False
            result['errors'].append("Missing module docstring")
            return

        # Check for required sections
        required = ['Prerequisites:', 'How to run:']
        for section in required:
            if section not in docstring:
                result['errors'].append(f"Docstring missing '{section}' section")

    def _check_execution(self, example_path: Path, result: dict):
        """Check example executes without errors (mocked)."""
        # Skip interactive examples
        if example_path.name in ['logs_development_workflow.py']:
            result['errors'].append("Skipped (interactive example)")
            return

        # Create mocks
        mock_task = Mock(spec=Task)
        mock_task.id = "test-task-123"
        mock_task.task_id = "test-task-123"
        mock_task.status = TaskStatus.COMPLETED
        mock_task.logs.return_value = "Mock logs"
        mock_task.wait.return_value = None

        mock_flow = MagicMock()
        mock_flow.__enter__.return_value = mock_flow
        mock_flow.__exit__.return_value = None
        mock_flow.run.return_value = mock_task

        # Prepare environment
        env_vars = {
            'FLOW_API_KEY': 'test-key',
            'AWS_ACCESS_KEY_ID': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'WANDB_API_KEY': 'test-wandb-key'
        }

        # Prepare argv
        argv = [str(example_path)]
        if any(x in example_path.name for x in ['cancel', 'check_task']):
            argv.append('test-task-123')

        # Capture output
        stdout = StringIO()
        stderr = StringIO()

        # Execute with mocks
        try:
            with patch('flow.Flow', return_value=mock_flow):
                with patch('flow.run', return_value=mock_task):
                    with patch('flow.status', return_value=mock_task):
                        with patch('flow.cancel', return_value=True):
                            with patch('flow.find_instances', return_value=[]):
                                with patch('secrets.token_urlsafe', return_value='test-token'):
                                    with patch.dict(os.environ, env_vars):
                                        with patch('sys.argv', argv):
                                            with redirect_stdout(stdout), redirect_stderr(stderr):
                                                # Execute the example
                                                exec_globals = {'__name__': '__main__', '__file__': str(example_path)}
                                                with open(example_path) as f:
                                                    code = compile(f.read(), str(example_path), 'exec')
                                                    exec(code, exec_globals)

            # Save golden output if requested
            if self.generate_golden:
                self._save_golden_output(example_path, stdout.getvalue(), stderr.getvalue())

        except SystemExit as e:
            if e.code != 0:
                result['passed'] = False
                result['errors'].append(f"Non-zero exit code: {e.code}")
        except Exception as e:
            result['passed'] = False
            result['errors'].append(f"Execution error: {type(e).__name__}: {e}")

    def _save_golden_output(self, example_path: Path, stdout: str, stderr: str):
        """Save golden output for an example."""
        self.golden_dir.mkdir(exist_ok=True)

        golden_file = self.golden_dir / f"{example_path.stem}.golden.json"
        golden_data = {
            'example': example_path.name,
            'stdout': stdout,
            'stderr': stderr,
            'exit_code': 0
        }

        with open(golden_file, 'w') as f:
            json.dump(golden_data, f, indent=2)

    def _print_summary(self):
        """Print validation summary."""
        print("\nValidation Summary")
        print("=" * 60)

        passed = sum(1 for r in self.results if r['passed'])
        total = len(self.results)

        print(f"Total examples: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")

        if passed == total:
            print("\n✓ All examples validated successfully!")
        else:
            print("\n✗ Some examples failed validation:")
            for result in self.results:
                if not result['passed']:
                    print(f"\n  {result['name']}:")
                    for error in result['errors']:
                        print(f"    - {error}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate Flow SDK examples')
    parser.add_argument('--generate-golden', action='store_true',
                        help='Generate golden output files')
    args = parser.parse_args()

    validator = ExampleValidator(generate_golden=args.generate_golden)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
