"""Example validator that tests examples serve their educational purpose.

Following the philosophy: Examples are documentation, not just code.
Test that they teach the right patterns, not that they execute perfectly.
"""

import ast
import sys
from pathlib import Path
from typing import Set

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class ExampleValidator:
    """Validate examples teach correct API usage patterns."""

    def __init__(self):
        self.examples_dir = Path(__file__).parent.parent / "examples"

    def _parse_example(self, path: Path) -> ast.AST:
        """Parse example file into AST."""
        with open(path) as f:
            return ast.parse(f.read(), filename=str(path))

    def _has_main_function(self, tree: ast.AST) -> bool:
        """Check if example has a main() function."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                return True
        return False

    def _has_main_guard(self, tree: ast.AST) -> bool:
        """Check if example has if __name__ == '__main__' guard."""
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for __name__ == "__main__" pattern
                if (isinstance(node.test, ast.Compare) and
                    isinstance(node.test.left, ast.Name) and
                    node.test.left.id == "__name__" and
                    isinstance(node.test.comparators[0], ast.Constant) and
                    node.test.comparators[0].value == "__main__"):
                    return True
        return False

    def _get_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all imports from the example."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.add(f"{module}.{alias.name}" if module else alias.name)
        return imports

    def _has_error_handling(self, tree: ast.AST) -> bool:
        """Check if example demonstrates error handling."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                return True
        return False

    def _demonstrates_pattern(self, tree: ast.AST, pattern: str) -> bool:
        """Check if example demonstrates a specific pattern."""
        patterns = {
            "context_manager": self._has_context_manager_usage,
            "task_config": self._uses_task_config,
            "error_handling": self._has_error_handling,
            "logging": self._has_logging_pattern,
            "cli_args": self._has_argparse_usage,
        }

        checker = patterns.get(pattern)
        return checker(tree) if checker else False

    def _has_context_manager_usage(self, tree: ast.AST) -> bool:
        """Check for 'with Flow() as client:' pattern."""
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if (isinstance(item.context_expr, ast.Call) and
                        isinstance(item.context_expr.func, ast.Name) and
                        item.context_expr.func.id == "Flow"):
                        return True
        return False

    def _uses_task_config(self, tree: ast.AST) -> bool:
        """Check if example uses TaskConfig."""
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == "TaskConfig"):
                return True
        return False

    def _has_logging_pattern(self, tree: ast.AST) -> bool:
        """Check if example shows output/logging."""
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and
                isinstance(node.func, ast.Name) and
                node.func.id == "print"):
                return True
        return False

    def _has_argparse_usage(self, tree: ast.AST) -> bool:
        """Check if example uses argparse for CLI."""
        imports = self._get_imports(tree)
        return "argparse" in imports

    def _has_docstring(self, tree: ast.AST) -> str:
        """Get module docstring if present."""
        return ast.get_docstring(tree) or ""


class TestExampleStructure:
    """Test that examples have correct structure."""

    def setup_method(self):
        """Set up validator for each test."""
        self.validator = ExampleValidator()

    def test_all_examples_have_main_function(self):
        """Every example should have a main() function."""
        for example in self.validator.examples_dir.glob("*.py"):
            if example.name == "__init__.py":
                continue

            tree = self.validator._parse_example(example)
            assert self.validator._has_main_function(tree), \
                f"{example.name} missing main() function"

    def test_all_examples_have_main_guard(self):
        """Every example should have if __name__ == '__main__' guard."""
        for example in self.validator.examples_dir.glob("*.py"):
            if example.name == "__init__.py":
                continue

            tree = self.validator._parse_example(example)
            assert self.validator._has_main_guard(tree), \
                f"{example.name} missing if __name__ == '__main__' guard"

    def test_all_examples_have_docstrings(self):
        """Every example should have a descriptive docstring."""
        for example in self.validator.examples_dir.glob("*.py"):
            if example.name == "__init__.py":
                continue

            tree = self.validator._parse_example(example)
            docstring = self.validator._has_docstring(tree)
            assert docstring, f"{example.name} missing module docstring"
            assert len(docstring) >= 50, \
                f"{example.name} docstring too short: {len(docstring)} chars"

    def test_examples_import_from_flow(self):
        """Every example should import from flow package."""
        for example in self.validator.examples_dir.glob("*.py"):
            if example.name == "__init__.py":
                continue

            tree = self.validator._parse_example(example)
            imports = self.validator._get_imports(tree)

            # Check for flow imports
            has_flow_import = any("flow" in imp for imp in imports)
            assert has_flow_import, \
                f"{example.name} doesn't import from flow package"


class TestExamplePatterns:
    """Test that examples demonstrate correct patterns."""

    def setup_method(self):
        """Set up validator for each test."""
        self.validator = ExampleValidator()

    # Define what patterns each example should demonstrate
    EXPECTED_PATTERNS = {
        "01_verify_instance.py": ["context_manager", "task_config", "error_handling"],
        "02_jupyter_server.py": ["context_manager", "task_config", "logging"],
        "03_multi_node_training.py": ["task_config", "logging"],
        "04_s3_data_access.py": ["task_config", "error_handling"],
        "create_gpu_task.py": ["task_config", "cli_args", "logging"],
        "list_available_instances.py": ["context_manager", "cli_args", "error_handling"],
        "check_task_status.py": ["context_manager", "cli_args", "error_handling"],
        "cancel_task.py": ["context_manager", "cli_args", "error_handling"],
    }

    def test_examples_demonstrate_expected_patterns(self):
        """Each example should demonstrate its expected patterns."""
        for example_name, expected_patterns in self.EXPECTED_PATTERNS.items():
            example_path = self.validator.examples_dir / example_name
            if not example_path.exists():
                continue

            tree = self.validator._parse_example(example_path)

            for pattern in expected_patterns:
                assert self.validator._demonstrates_pattern(tree, pattern), \
                    f"{example_name} doesn't demonstrate {pattern} pattern"

    def test_gpu_examples_show_instance_selection(self):
        """GPU examples should show how to select instances."""
        gpu_examples = [
            "01_verify_instance.py",
            "02_jupyter_server.py",
            "03_multi_node_training.py",
            "create_gpu_task.py"
        ]

        for example_name in gpu_examples:
            example_path = self.validator.examples_dir / example_name
            if not example_path.exists():
                continue

            with open(example_path) as f:
                content = f.read()

            # Should mention instance types
            assert any(gpu in content for gpu in ["a100", "h100", "instance_type"]), \
                f"{example_name} doesn't show instance selection"

    def test_examples_handle_credentials_gracefully(self):
        """Examples should handle missing credentials gracefully."""
        credential_examples = [
            "01_verify_instance.py",
            "04_s3_data_access.py",
        ]

        for example_name in credential_examples:
            example_path = self.validator.examples_dir / example_name
            if not example_path.exists():
                continue

            tree = self.validator._parse_example(example_path)

            # Should have error handling
            assert self.validator._has_error_handling(tree), \
                f"{example_name} doesn't handle errors"

            # Should mention credentials in error messages
            with open(example_path) as f:
                content = f.read()

            assert any(term in content.lower() for term in
                      ["credential", "api key", "auth", "flow init"]), \
                f"{example_name} doesn't guide users on credentials"


class TestExampleUsability:
    """Test that examples are usable as learning resources."""

    def setup_method(self):
        """Set up test data."""
        self.examples_dir = Path(__file__).parent.parent / "examples"

    def test_examples_are_self_contained(self):
        """Each example should be runnable on its own."""
        for example in self.examples_dir.glob("*.py"):
            if example.name == "__init__.py":
                continue

            with open(example) as f:
                content = f.read()

            # Should not reference other example files
            assert "../examples/" not in content, \
                f"{example.name} references other examples"

            # Should not have complex dependencies
            assert "requirements.txt" not in content, \
                f"{example.name} references external requirements"

    def test_examples_have_clear_output(self):
        """Examples should show what they're doing."""
        for example in self.examples_dir.glob("*.py"):
            if example.name == "__init__.py":
                continue

            with open(example) as f:
                content = f.read()

            # Should have print statements explaining what's happening
            assert "print(" in content, \
                f"{example.name} doesn't show output to user"

    def test_example_names_are_descriptive(self):
        """Example filenames should describe what they do."""
        expected_examples = {
            "01_verify_instance.py",
            "02_jupyter_server.py",
            "03_multi_node_training.py",
            "04_s3_data_access.py",
            "create_gpu_task.py",
            "list_available_instances.py",
            "check_task_status.py",
            "cancel_task.py",
        }

        actual_examples = {f.name for f in self.examples_dir.glob("*.py")
                          if f.name != "__init__.py"}

        # All examples should have descriptive names
        for example in actual_examples:
            # Name should indicate what it does
            assert any(keyword in example.lower() for keyword in
                      ["verify", "jupyter", "training", "s3", "create",
                       "list", "check", "cancel", "local", "test", "log", "workflow"]), \
                f"{example} has non-descriptive name"
