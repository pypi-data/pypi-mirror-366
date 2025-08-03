"""Test dependency analysis for Flow SDK.

This script analyzes test files to identify:
1. Shared fixtures and their usage
2. Module-level state that persists between tests
3. Tests that depend on external resources
4. Order dependencies between test methods
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


@dataclass
class DependencyInfo:
    """Information about test dependencies."""
    file_path: Path
    fixtures_used: Set[str] = field(default_factory=set)
    fixtures_defined: Set[str] = field(default_factory=set)
    class_fixtures: Set[str] = field(default_factory=set)
    session_fixtures: Set[str] = field(default_factory=set)
    module_globals: Set[str] = field(default_factory=set)
    external_dependencies: Set[str] = field(default_factory=set)
    setup_teardown_methods: Set[str] = field(default_factory=set)
    shared_state_risks: List[str] = field(default_factory=list)
    test_classes: List[str] = field(default_factory=list)
    test_functions: List[str] = field(default_factory=list)


class DependencyAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze test dependencies."""
    
    def __init__(self):
        self.info = DependencyInfo(file_path=Path())
        self.current_class = None
        self.in_fixture = False
        
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        # Check if it's a fixture
        for decorator in node.decorator_list:
            if self._is_fixture_decorator(decorator):
                self.info.fixtures_defined.add(node.name)
                self.in_fixture = True
                # Check fixture scope
                scope = self._get_fixture_scope(decorator)
                if scope == "class":
                    self.info.class_fixtures.add(node.name)
                elif scope == "session":
                    self.info.session_fixtures.add(node.name)
                    
        # Check if it's a test function
        if node.name.startswith("test_"):
            if self.current_class:
                self.info.test_functions.append(f"{self.current_class}.{node.name}")
            else:
                self.info.test_functions.append(node.name)
                
            # Extract fixtures from arguments
            for arg in node.args.args:
                if arg.arg not in ["self", "cls"]:
                    self.info.fixtures_used.add(arg.arg)
                    
        # Check for setup/teardown methods
        if node.name in ["setup_method", "teardown_method", "setup_class", 
                        "teardown_class", "setup", "teardown"]:
            self.info.setup_teardown_methods.add(node.name)
            self.info.shared_state_risks.append(
                f"Uses {node.name} which may create order dependencies"
            )
            
        self.generic_visit(node)
        self.in_fixture = False
        
    def visit_ClassDef(self, node):
        """Visit class definitions."""
        if node.name.startswith("Test"):
            self.info.test_classes.append(node.name)
            self.current_class = node.name
            
            # Check for class-level attributes
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            self.info.shared_state_risks.append(
                                f"Class {node.name} has class-level attribute: {target.id}"
                            )
                            
        self.generic_visit(node)
        self.current_class = None
        
    def visit_Assign(self, node):
        """Visit assignments to find module-level state."""
        if self.current_class is None and not self.in_fixture:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    self.info.module_globals.add(target.id)
                    
        self.generic_visit(node)
        
    def visit_Call(self, node):
        """Visit function calls to find external dependencies."""
        # Check for environment variable access
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "os" and node.func.attr == "environ":
                    self.info.external_dependencies.add("os.environ")
                elif node.func.value.id == "os" and node.func.attr in ["makedirs", "remove"]:
                    self.info.external_dependencies.add("filesystem")
                    
        # Check for network calls
        if hasattr(node.func, "attr"):
            if node.func.attr in ["request", "get", "post", "put", "delete"]:
                self.info.external_dependencies.add("network")
                
        self.generic_visit(node)
        
    def _is_fixture_decorator(self, decorator):
        """Check if decorator is a pytest fixture."""
        if isinstance(decorator, ast.Name) and decorator.id == "fixture":
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == "fixture":
            return True
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == "fixture":
                return True
            if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "fixture":
                return True
        return False
        
    def _get_fixture_scope(self, decorator):
        """Extract fixture scope from decorator."""
        if isinstance(decorator, ast.Call):
            for keyword in decorator.keywords:
                if keyword.arg == "scope":
                    if isinstance(keyword.value, ast.Constant):
                        return keyword.value.value
        return "function"


def analyze_test_file(file_path: Path) -> DependencyInfo:
    """Analyze a single test file for dependencies."""
    with open(file_path, "r") as f:
        content = f.read()
        
    try:
        tree = ast.parse(content)
        analyzer = DependencyAnalyzer()
        analyzer.info.file_path = file_path
        analyzer.visit(tree)
        
        # Additional regex-based analysis for patterns AST might miss
        # Check for pytest.mark.usefixtures
        usefixtures_pattern = r'@pytest\.mark\.usefixtures\((.*?)\)'
        for match in re.finditer(usefixtures_pattern, content):
            fixtures = match.group(1).replace('"', '').replace("'", '').split(',')
            analyzer.info.fixtures_used.update(f.strip() for f in fixtures)
            
        # Check for global test state
        if "global " in content:
            analyzer.info.shared_state_risks.append("Uses global keyword")
            
        # Check for time.sleep (indicates potential race conditions)
        if "time.sleep" in content or "sleep(" in content:
            analyzer.info.shared_state_risks.append("Uses sleep - potential race condition")
            
        return analyzer.info
    except SyntaxError:
        # Return empty info if file has syntax errors
        return DependencyInfo(file_path=file_path)


def generate_dependency_report(test_dir: Path) -> Dict[str, Any]:
    """Generate comprehensive dependency report for all test files."""
    report = {
        "fixture_usage": {},
        "shared_fixtures": {},
        "risky_patterns": {},
        "external_dependencies": {},
        "test_counts": {},
    }
    
    all_fixtures_defined = {}
    all_fixtures_used = {}
    
    # Analyze all test files
    for test_file in test_dir.rglob("test_*.py"):
        if "__pycache__" in str(test_file):
            continue
            
        info = analyze_test_file(test_file)
        rel_path = test_file.relative_to(test_dir)
        
        # Track fixture definitions and usage
        for fixture in info.fixtures_defined:
            if fixture not in all_fixtures_defined:
                all_fixtures_defined[fixture] = []
            all_fixtures_defined[fixture].append(str(rel_path))
            
        for fixture in info.fixtures_used:
            if fixture not in all_fixtures_used:
                all_fixtures_used[fixture] = []
            all_fixtures_used[fixture].append(str(rel_path))
            
        # Track risky patterns
        if info.shared_state_risks:
            report["risky_patterns"][str(rel_path)] = info.shared_state_risks
            
        # Track external dependencies
        if info.external_dependencies:
            report["external_dependencies"][str(rel_path)] = list(info.external_dependencies)
            
        # Track test counts
        report["test_counts"][str(rel_path)] = {
            "classes": len(info.test_classes),
            "functions": len(info.test_functions),
            "fixtures_defined": len(info.fixtures_defined),
            "session_fixtures": len(info.session_fixtures),
            "class_fixtures": len(info.class_fixtures),
        }
        
    # Find shared fixtures (used by multiple files)
    for fixture, users in all_fixtures_used.items():
        if len(users) > 1:
            report["shared_fixtures"][fixture] = {
                "used_by": users,
                "defined_in": all_fixtures_defined.get(fixture, ["external"]),
            }
            
    # Analyze fixture dependencies
    report["fixture_usage"] = {
        "most_used": sorted(
            [(f, len(users)) for f, users in all_fixtures_used.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10],
        "session_scoped": [
            f for f, files in all_fixtures_defined.items()
            if any(analyze_test_file(test_dir / files[0]).session_fixtures)
        ],
    }
    
    return report


def print_dependency_report(report: Dict[str, Any]):
    """Print human-readable dependency report."""
    print("=" * 80)
    print("TEST DEPENDENCY ANALYSIS REPORT")
    print("=" * 80)
    
    print("\n## SHARED FIXTURES (potential order dependencies)")
    print("-" * 40)
    for fixture, info in report["shared_fixtures"].items():
        print(f"\n{fixture}:")
        print(f"  Defined in: {', '.join(info['defined_in'])}")
        print(f"  Used by: {', '.join(info['used_by'][:5])}")
        if len(info['used_by']) > 5:
            print(f"  ... and {len(info['used_by']) - 5} more files")
            
    print("\n## RISKY PATTERNS (test isolation concerns)")
    print("-" * 40)
    for file, risks in sorted(report["risky_patterns"].items()):
        print(f"\n{file}:")
        for risk in risks:
            print(f"  - {risk}")
            
    print("\n## EXTERNAL DEPENDENCIES")
    print("-" * 40)
    deps_by_type = {}
    for file, deps in report["external_dependencies"].items():
        for dep in deps:
            if dep not in deps_by_type:
                deps_by_type[dep] = []
            deps_by_type[dep].append(file)
            
    for dep_type, files in sorted(deps_by_type.items()):
        print(f"\n{dep_type}: {len(files)} files")
        for file in files[:3]:
            print(f"  - {file}")
        if len(files) > 3:
            print(f"  ... and {len(files) - 3} more")
            
    print("\n## FIXTURE USAGE STATISTICS")
    print("-" * 40)
    print("\nMost used fixtures:")
    for fixture, count in report["fixture_usage"]["most_used"]:
        print(f"  {fixture}: {count} files")
        
    print("\n## TEST FILE STATISTICS")
    print("-" * 40)
    total_classes = sum(info["classes"] for info in report["test_counts"].values())
    total_functions = sum(info["functions"] for info in report["test_counts"].values())
    total_fixtures = sum(info["fixtures_defined"] for info in report["test_counts"].values())
    
    print(f"Total test files: {len(report['test_counts'])}")
    print(f"Total test classes: {total_classes}")
    print(f"Total test functions: {total_functions}")
    print(f"Total fixtures defined: {total_fixtures}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run analysis on the tests directory
    test_dir = Path(__file__).parent.parent
    report = generate_dependency_report(test_dir)
    print_dependency_report(report)
    
    # Save detailed report as JSON
    import json
    with open(test_dir / "analysis" / "dependency_report.json", "w") as f:
        # Convert sets to lists for JSON serialization
        def convert_sets(obj):
            if isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets(item) for item in obj]
            return obj
            
        json.dump(convert_sets(report), f, indent=2)
        
    print(f"\nDetailed report saved to: {test_dir / 'analysis' / 'dependency_report.json'}")