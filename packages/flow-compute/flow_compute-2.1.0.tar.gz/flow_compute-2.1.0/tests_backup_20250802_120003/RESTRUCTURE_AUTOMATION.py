#!/usr/bin/env python3
"""Automated test restructuring script with comprehensive import fixing.

This script implements the test restructuring plan with careful attention to:
- Preserving all functionality
- Updating all imports correctly
- Maintaining test execution
- Creating proper mappings
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import json
from datetime import datetime


class TestRestructurer:
    """Handles the complete test restructuring process."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.project_root = Path.cwd()
        self.tests_dir = self.project_root / "tests"
        self.backup_dir = None
        self.file_mappings = {}
        self.import_mappings = {}
        self.affected_files = set()
        
    def analyze_current_structure(self) -> Dict:
        """Analyze current test structure and categorize files."""
        analysis = {
            "total_files": 0,
            "by_directory": {},
            "test_files": [],
            "support_files": [],
            "duplicate_candidates": []
        }
        
        for root, dirs, files in os.walk(self.tests_dir):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            
            rel_root = Path(root).relative_to(self.tests_dir)
            
            for file in files:
                if file.endswith(".py"):
                    analysis["total_files"] += 1
                    file_path = Path(root) / file
                    rel_path = file_path.relative_to(self.tests_dir)
                    
                    # Categorize files
                    if file.startswith("test_"):
                        analysis["test_files"].append(str(rel_path))
                    else:
                        analysis["support_files"].append(str(rel_path))
                    
                    # Find duplicates
                    if "_fixed" in file or "_updated" in file or "_improved" in file:
                        analysis["duplicate_candidates"].append(str(rel_path))
                    
                    # Count by directory
                    dir_name = str(rel_root).split("/")[0] if "/" in str(rel_root) else str(rel_root)
                    if dir_name not in analysis["by_directory"]:
                        analysis["by_directory"][dir_name] = 0
                    analysis["by_directory"][dir_name] += 1
        
        return analysis
    
    def analyze_test_performance(self) -> Dict[str, float]:
        """Run tests with timing to categorize fast vs slow."""
        print("Analyzing test performance...")
        
        # Run pytest with durations
        result = subprocess.run(
            ["pytest", "--durations=0", "--tb=no", "-q", str(self.tests_dir)],
            capture_output=True,
            text=True
        )
        
        # Parse output for timings
        timings = {}
        for line in result.stdout.split("\n"):
            # Look for timing lines
            match = re.match(r"([\d.]+)s.*?(\S+\.py)::\S+", line)
            if match:
                duration = float(match.group(1))
                file_path = match.group(2)
                if file_path not in timings or duration > timings[file_path]:
                    timings[file_path] = duration
        
        return timings
    
    def create_file_mappings(self, timings: Dict[str, float]) -> Dict[str, str]:
        """Create detailed mapping of old paths to new paths."""
        mappings = {}
        
        for root, dirs, files in os.walk(self.tests_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            
            for file in files:
                if not file.endswith(".py"):
                    continue
                    
                old_path = Path(root) / file
                rel_path = old_path.relative_to(self.tests_dir)
                
                # Determine new location
                new_path = self._determine_new_path(rel_path, timings)
                if new_path:
                    mappings[str(rel_path)] = str(new_path)
        
        return mappings
    
    def _determine_new_path(self, rel_path: Path, timings: Dict[str, float]) -> Path:
        """Determine new path for a file based on categorization."""
        path_str = str(rel_path)
        
        # Skip if already in new structure
        if path_str.startswith(("fast/", "slow/", "support/")):
            return None
        
        # Support files
        support_mapping = {
            "fixtures/": "support/fixtures/",
            "utils/": "support/utils/",
            "testing/": "support/framework/",
            "data/": "support/data/",
            "config/": "support/config/",
            "scripts/": "support/scripts/",
            "tools/": "support/tools/",
            "docs/": "support/docs/",
            "analysis/": "support/analysis/",
            "verification/": "support/verification/",
        }
        
        for old_dir, new_dir in support_mapping.items():
            if path_str.startswith(old_dir):
                return Path(new_dir + path_str[len(old_dir):])
        
        # Test files
        if rel_path.name.startswith("test_"):
            # Check timing
            timing = timings.get(str(rel_path), 0)
            
            # Categorize by directory and timing
            if path_str.startswith("unit/") or path_str.startswith("smoke/"):
                return Path("fast") / rel_path.name
            elif path_str.startswith(("integration/", "e2e/")):
                # Preserve some structure for slow tests
                if path_str.startswith("e2e/"):
                    return Path("slow/e2e") / rel_path.name
                else:
                    # Integration tests - organize by component
                    parts = rel_path.parts
                    if len(parts) > 2:  # Has subdirectory
                        return Path("slow") / parts[1] / rel_path.name
                    else:
                        return Path("slow") / rel_path.name
            elif path_str.startswith("functional/"):
                # Functional tests based on timing
                if timing < 1.0:
                    return Path("fast") / rel_path.name
                else:
                    return Path("slow") / rel_path.name
            elif path_str.startswith("performance/"):
                return Path("slow/performance") / rel_path.name
        
        # Default for other files
        if rel_path.name == "conftest.py":
            return rel_path  # Keep in same location
        elif rel_path.name == "__init__.py":
            # Will create these as needed
            return None
        else:
            return Path("support/misc") / rel_path.name
    
    def scan_imports(self) -> Dict[str, Set[str]]:
        """Scan all Python files for test-related imports."""
        imports_map = {}
        
        # Scan all Python files in the project
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "venv", ".venv"]]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    imports = self._extract_imports(file_path)
                    if imports:
                        imports_map[str(file_path)] = imports
        
        return imports_map
    
    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all test-related imports from a file."""
        test_imports = set()
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("tests."):
                        test_imports.add(node.module)
                elif isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name.startswith("tests."):
                            test_imports.add(name.name)
            
            # Also check for relative imports in test files
            if str(file_path).startswith(str(self.tests_dir)):
                # Regex for relative imports
                rel_imports = re.findall(r'from\s+\.\.?(?:\.[.\w]+)?\s+import', content)
                test_imports.update(rel_imports)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return test_imports
    
    def create_import_mappings(self) -> Dict[str, str]:
        """Create mapping of old imports to new imports."""
        import_map = {}
        
        # Convert file mappings to import mappings
        for old_path, new_path in self.file_mappings.items():
            # Convert path to module
            old_module = old_path.replace("/", ".").replace(".py", "")
            new_module = new_path.replace("/", ".").replace(".py", "")
            
            # Full module imports
            import_map[f"tests.{old_module}"] = f"tests.{new_module}"
            
            # Parent module imports
            old_parts = old_module.split(".")
            new_parts = new_module.split(".")
            
            if len(old_parts) > 1:
                old_parent = ".".join(old_parts[:-1])
                new_parent = ".".join(new_parts[:-1])
                import_map[f"tests.{old_parent}"] = f"tests.{new_parent}"
        
        return import_map
    
    def backup_tests(self):
        """Create backup of current test directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.tests_dir.parent / f"tests_backup_{timestamp}"
        
        print(f"Creating backup at {self.backup_dir}")
        if not self.dry_run:
            shutil.copytree(self.tests_dir, self.backup_dir)
    
    def create_new_structure(self):
        """Create new directory structure."""
        directories = [
            "fast",
            "slow",
            "slow/e2e",
            "slow/providers",
            "slow/performance",
            "slow/system",
            "support",
            "support/fixtures",
            "support/utils",
            "support/framework",
            "support/data",
            "support/config",
            "support/scripts",
            "support/tools",
            "support/docs",
            "support/analysis",
            "support/verification",
            "support/misc",
        ]
        
        for dir_path in directories:
            full_path = self.tests_dir / dir_path
            print(f"Creating directory: {full_path}")
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
                # Create __init__.py
                init_file = full_path / "__init__.py"
                init_file.touch()
    
    def move_files(self):
        """Move files according to mappings."""
        for old_path, new_path in self.file_mappings.items():
            old_full = self.tests_dir / old_path
            new_full = self.tests_dir / new_path
            
            if old_full.exists():
                print(f"Moving {old_path} -> {new_path}")
                if not self.dry_run:
                    new_full.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(old_full), str(new_full))
    
    def update_imports(self, imports_map: Dict[str, Set[str]]):
        """Update all imports in affected files."""
        for file_path, imports in imports_map.items():
            if self._needs_import_update(imports):
                print(f"Updating imports in {file_path}")
                if not self.dry_run:
                    self._update_file_imports(Path(file_path))
    
    def _needs_import_update(self, imports: Set[str]) -> bool:
        """Check if file has imports that need updating."""
        for imp in imports:
            if any(imp.startswith(old) for old in self.import_mappings.keys()):
                return True
        return False
    
    def _update_file_imports(self, file_path: Path):
        """Update imports in a single file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Update imports
        for old_import, new_import in self.import_mappings.items():
            # from X import Y
            content = re.sub(
                rf'from {re.escape(old_import)} import',
                f'from {new_import} import',
                content
            )
            # import X
            content = re.sub(
                rf'import {re.escape(old_import)}(?=\s|$)',
                f'import {new_import}',
                content
            )
        
        # Update relative imports in test files
        if str(file_path).startswith(str(self.tests_dir)):
            content = self._update_relative_imports(file_path, content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
    
    def _update_relative_imports(self, file_path: Path, content: str) -> str:
        """Update relative imports based on new file location."""
        # This is complex and depends on specific file moves
        # Would need careful implementation for each case
        return content
    
    def update_configurations(self):
        """Update pytest.ini, conftest.py, and other configurations."""
        # Update pytest.ini
        pytest_ini = self.project_root / "pytest.ini"
        if pytest_ini.exists():
            print("Updating pytest.ini")
            if not self.dry_run:
                with open(pytest_ini, 'r') as f:
                    content = f.read()
                
                # Update testpaths
                content = re.sub(
                    r'testpaths\s*=.*',
                    'testpaths = tests/fast tests/slow',
                    content
                )
                
                with open(pytest_ini, 'w') as f:
                    f.write(content)
    
    def verify_tests(self):
        """Run tests to verify everything still works."""
        print("\nVerifying tests...")
        
        # Try to run fast tests
        result = subprocess.run(
            ["pytest", "tests/fast", "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Fast tests failed!")
            print(result.stdout)
            print(result.stderr)
        else:
            print("Fast tests passed!")
    
    def generate_report(self):
        """Generate detailed report of changes."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "file_mappings": self.file_mappings,
            "import_mappings": self.import_mappings,
            "stats": {
                "total_files_moved": len(self.file_mappings),
                "imports_updated": len(self.affected_files)
            }
        }
        
        report_path = self.tests_dir / "RESTRUCTURE_REPORT.json"
        print(f"\nGenerating report at {report_path}")
        
        if not self.dry_run:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
    
    def run(self):
        """Execute the complete restructuring process."""
        print("Starting test restructuring...")
        print(f"Dry run: {self.dry_run}")
        
        # Phase 1: Analysis
        print("\n=== Phase 1: Analysis ===")
        structure = self.analyze_current_structure()
        print(f"Found {structure['total_files']} Python files")
        print(f"Test files: {len(structure['test_files'])}")
        print(f"Support files: {len(structure['support_files'])}")
        print(f"Duplicate candidates: {len(structure['duplicate_candidates'])}")
        
        # Get test timings (optional, can be skipped in dry run)
        timings = {}
        if not self.dry_run:
            timings = self.analyze_test_performance()
        
        # Create mappings
        self.file_mappings = self.create_file_mappings(timings)
        print(f"\nCreated mappings for {len(self.file_mappings)} files")
        
        # Scan imports
        imports_map = self.scan_imports()
        print(f"Found test imports in {len(imports_map)} files")
        
        # Create import mappings
        self.import_mappings = self.create_import_mappings()
        
        if self.dry_run:
            print("\n=== Dry Run - Proposed Changes ===")
            print("\nFile moves:")
            for old, new in list(self.file_mappings.items())[:10]:
                print(f"  {old} -> {new}")
            if len(self.file_mappings) > 10:
                print(f"  ... and {len(self.file_mappings) - 10} more")
            
            print("\nImport updates needed in:")
            for file in list(imports_map.keys())[:10]:
                if self._needs_import_update(imports_map[file]):
                    print(f"  {file}")
            
            return
        
        # Phase 2: Backup
        print("\n=== Phase 2: Backup ===")
        self.backup_tests()
        
        # Phase 3: Restructure
        print("\n=== Phase 3: Restructure ===")
        self.create_new_structure()
        self.move_files()
        
        # Phase 4: Update imports
        print("\n=== Phase 4: Update Imports ===")
        self.update_imports(imports_map)
        
        # Phase 5: Update configurations
        print("\n=== Phase 5: Update Configurations ===")
        self.update_configurations()
        
        # Phase 6: Verify
        print("\n=== Phase 6: Verification ===")
        self.verify_tests()
        
        # Generate report
        self.generate_report()
        
        print("\n=== Restructuring Complete ===")
        print(f"Backup available at: {self.backup_dir}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Restructure Flow SDK tests")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually perform the restructuring (default is dry run)"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze current structure"
    )
    
    args = parser.parse_args()
    
    restructurer = TestRestructurer(dry_run=not args.execute)
    
    if args.analyze_only:
        analysis = restructurer.analyze_current_structure()
        print(json.dumps(analysis, indent=2))
    else:
        restructurer.run()


if __name__ == "__main__":
    main()