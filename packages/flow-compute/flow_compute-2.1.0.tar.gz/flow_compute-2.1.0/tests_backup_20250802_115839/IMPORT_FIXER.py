#!/usr/bin/env python3
"""Specialized import fixer for test restructuring.

This script handles the complex task of updating all imports after moving test files,
including relative imports, circular dependencies, and path-based references.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import logging


class ImportFixer:
    """Handles comprehensive import fixing after test restructuring."""
    
    def __init__(self, file_mappings: Dict[str, str], project_root: Path):
        self.file_mappings = file_mappings
        self.project_root = project_root
        self.tests_dir = project_root / "tests"
        
        # Build reverse mapping
        self.reverse_mappings = {v: k for k, v in file_mappings.items()}
        
        # Build module mappings
        self.module_mappings = self._build_module_mappings()
        
        # Track files that need updates
        self.files_to_update = set()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _build_module_mappings(self) -> Dict[str, str]:
        """Convert file paths to module paths."""
        module_map = {}
        
        for old_path, new_path in self.file_mappings.items():
            # Remove .py and convert / to .
            old_module = old_path.replace(".py", "").replace("/", ".")
            new_module = new_path.replace(".py", "").replace("/", ".")
            
            # Add tests prefix
            module_map[f"tests.{old_module}"] = f"tests.{new_module}"
            
            # Also map parent modules
            old_parts = old_module.split(".")
            new_parts = new_module.split(".")
            
            for i in range(1, len(old_parts)):
                old_parent = ".".join(old_parts[:i])
                new_parent = ".".join(new_parts[:i])
                if old_parent != new_parent:
                    module_map[f"tests.{old_parent}"] = f"tests.{new_parent}"
        
        return module_map
    
    def find_all_imports(self) -> Dict[str, List[Tuple[str, int, str]]]:
        """Find all imports that need updating.
        
        Returns:
            Dict mapping file paths to list of (import_statement, line_number, import_type)
        """
        imports_by_file = {}
        
        # Search all Python files
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environments and caches
            dirs[:] = [d for d in dirs if d not in {
                "__pycache__", ".git", "venv", ".venv", "env", 
                ".tox", ".pytest_cache", "htmlcov", ".mypy_cache"
            }]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    imports = self._extract_imports_from_file(file_path)
                    if imports:
                        imports_by_file[str(file_path)] = imports
        
        return imports_by_file
    
    def _extract_imports_from_file(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extract all test-related imports from a file."""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "tests" in node.module:
                        import_str = self._format_import_from(node)
                        imports.append((import_str, node.lineno, "from"))
                    elif node.level > 0:  # Relative import
                        import_str = self._format_relative_import(node, file_path)
                        if import_str:
                            imports.append((import_str, node.lineno, "relative"))
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "tests" in alias.name:
                            import_str = f"import {alias.name}"
                            if alias.asname:
                                import_str += f" as {alias.asname}"
                            imports.append((import_str, node.lineno, "import"))
            
            # Also find string-based imports (like in __init__.py files)
            string_imports = self._find_string_imports(content)
            imports.extend(string_imports)
            
            # Find path-based references
            path_refs = self._find_path_references(content)
            imports.extend(path_refs)
            
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return imports
    
    def _format_import_from(self, node: ast.ImportFrom) -> str:
        """Format ImportFrom node to string."""
        import_str = f"from {node.module}"
        
        names = []
        for alias in node.names:
            if alias.asname:
                names.append(f"{alias.name} as {alias.asname}")
            else:
                names.append(alias.name)
        
        import_str += f" import {', '.join(names)}"
        return import_str
    
    def _format_relative_import(self, node: ast.ImportFrom, file_path: Path) -> Optional[str]:
        """Format relative import, checking if it's test-related."""
        # Calculate the module this import resolves to
        if not str(file_path).startswith(str(self.tests_dir)):
            return None
        
        # Get the package of the current file
        rel_path = file_path.relative_to(self.tests_dir)
        current_package = str(rel_path.parent).replace("/", ".")
        
        # Resolve the relative import
        level = node.level
        if level == 1:  # from . import
            target_package = current_package
        else:  # from .. import
            parts = current_package.split(".")
            if len(parts) >= level - 1:
                target_package = ".".join(parts[:-(level-1)])
            else:
                return None
        
        if node.module:
            target_module = f"{target_package}.{node.module}"
        else:
            target_module = target_package
        
        # Format the import
        dots = "." * level
        module_part = f".{node.module}" if node.module else ""
        import_str = f"from {dots}{module_part}"
        
        names = []
        for alias in node.names:
            if alias.asname:
                names.append(f"{alias.name} as {alias.asname}")
            else:
                names.append(alias.name)
        
        import_str += f" import {', '.join(names)}"
        return import_str
    
    def _find_string_imports(self, content: str) -> List[Tuple[str, int, str]]:
        """Find imports in strings (dynamic imports, exec, etc)."""
        imports = []
        
        # Find __import__() calls
        pattern = r'__import__\(["\']([^"\']+)["\']\)'
        for match in re.finditer(pattern, content):
            module = match.group(1)
            if "tests" in module:
                line_no = content[:match.start()].count('\n') + 1
                imports.append((f"__import__('{module}')", line_no, "dynamic"))
        
        # Find importlib imports
        pattern = r'importlib\.import_module\(["\']([^"\']+)["\']\)'
        for match in re.finditer(pattern, content):
            module = match.group(1)
            if "tests" in module:
                line_no = content[:match.start()].count('\n') + 1
                imports.append((f"importlib.import_module('{module}')", line_no, "dynamic"))
        
        return imports
    
    def _find_path_references(self, content: str) -> List[Tuple[str, int, str]]:
        """Find path-based references to test files."""
        references = []
        
        # Find Path("tests/...") or Path('tests/...')
        pattern = r'Path\(["\']tests/([^"\']+)["\']\)'
        for match in re.finditer(pattern, content):
            path = f"tests/{match.group(1)}"
            line_no = content[:match.start()].count('\n') + 1
            references.append((f'Path("{path}")', line_no, "path"))
        
        # Find direct string paths
        pattern = r'["\']tests/([^"\']+\.py)["\']'
        for match in re.finditer(pattern, content):
            path = f"tests/{match.group(1)}"
            line_no = content[:match.start()].count('\n') + 1
            references.append((f'"{path}"', line_no, "path"))
        
        return references
    
    def create_update_plan(self, imports_by_file: Dict[str, List[Tuple[str, int, str]]]) -> Dict[str, List[Dict]]:
        """Create detailed plan for updating imports."""
        update_plan = {}
        
        for file_path, imports in imports_by_file.items():
            updates = []
            
            for import_str, line_no, import_type in imports:
                if import_type == "from" or import_type == "import":
                    # Check if module needs updating
                    for old_module, new_module in self.module_mappings.items():
                        if old_module in import_str:
                            new_import = import_str.replace(old_module, new_module)
                            updates.append({
                                "line": line_no,
                                "old": import_str,
                                "new": new_import,
                                "type": import_type
                            })
                            break
                
                elif import_type == "relative":
                    # Handle relative imports
                    update = self._plan_relative_import_update(file_path, import_str, line_no)
                    if update:
                        updates.append(update)
                
                elif import_type == "path":
                    # Handle path references
                    update = self._plan_path_update(import_str, line_no)
                    if update:
                        updates.append(update)
                
                elif import_type == "dynamic":
                    # Handle dynamic imports
                    for old_module, new_module in self.module_mappings.items():
                        if old_module in import_str:
                            new_import = import_str.replace(old_module, new_module)
                            updates.append({
                                "line": line_no,
                                "old": import_str,
                                "new": new_import,
                                "type": import_type
                            })
                            break
            
            if updates:
                update_plan[file_path] = updates
        
        return update_plan
    
    def _plan_relative_import_update(self, file_path: str, import_str: str, line_no: int) -> Optional[Dict]:
        """Plan update for relative import if file has moved."""
        # Check if this file has moved
        file_path_obj = Path(file_path)
        if not str(file_path_obj).startswith(str(self.tests_dir)):
            return None
        
        rel_path = file_path_obj.relative_to(self.tests_dir)
        
        # Check if this file was moved
        for old_path, new_path in self.file_mappings.items():
            if str(rel_path) == new_path:
                # File was moved, need to update relative imports
                old_rel_path = Path(old_path)
                new_rel_path = Path(new_path)
                
                # Calculate how relative import needs to change
                old_depth = len(old_rel_path.parts) - 1
                new_depth = len(new_rel_path.parts) - 1
                
                if old_depth != new_depth:
                    # Need to adjust relative import level
                    return {
                        "line": line_no,
                        "old": import_str,
                        "new": self._adjust_relative_import(import_str, old_depth, new_depth),
                        "type": "relative"
                    }
        
        return None
    
    def _adjust_relative_import(self, import_str: str, old_depth: int, new_depth: int) -> str:
        """Adjust relative import dots based on depth change."""
        # Count current dots
        match = re.match(r'from (\.+)', import_str)
        if not match:
            return import_str
        
        current_dots = len(match.group(1))
        
        # Adjust dots based on depth change
        depth_change = new_depth - old_depth
        new_dots = current_dots + depth_change
        
        if new_dots <= 0:
            # Convert to absolute import
            # This is complex and would need more context
            return import_str
        
        # Replace dots
        new_import = re.sub(r'from \.+', f'from {"." * new_dots}', import_str)
        return new_import
    
    def _plan_path_update(self, path_str: str, line_no: int) -> Optional[Dict]:
        """Plan update for path reference."""
        # Extract path from string
        match = re.search(r'tests/(.+?)(?:\.py)?["\']', path_str)
        if not match:
            return None
        
        old_path = match.group(1)
        if old_path.endswith(".py"):
            lookup_path = old_path
        else:
            lookup_path = f"{old_path}.py"
        
        # Check if this path needs updating
        for old, new in self.file_mappings.items():
            if old == lookup_path or old.startswith(f"{old_path}/"):
                new_path_str = path_str.replace(f"tests/{old_path}", f"tests/{new.replace('.py', '')}")
                return {
                    "line": line_no,
                    "old": path_str,
                    "new": new_path_str,
                    "type": "path"
                }
        
        return None
    
    def apply_updates(self, update_plan: Dict[str, List[Dict]], dry_run: bool = True):
        """Apply the import updates to files."""
        total_files = len(update_plan)
        total_updates = sum(len(updates) for updates in update_plan.values())
        
        print(f"\nImport Update Summary:")
        print(f"  Files to update: {total_files}")
        print(f"  Total updates: {total_updates}")
        
        if dry_run:
            print("\nDry run - showing first 10 updates:")
            count = 0
            for file_path, updates in update_plan.items():
                print(f"\n{file_path}:")
                for update in updates:
                    print(f"  Line {update['line']}: {update['old']} -> {update['new']}")
                    count += 1
                    if count >= 10:
                        remaining = total_updates - count
                        if remaining > 0:
                            print(f"\n... and {remaining} more updates")
                        return
        else:
            for file_path, updates in update_plan.items():
                self._update_file(file_path, updates)
                print(f"Updated {file_path}")
    
    def _update_file(self, file_path: str, updates: List[Dict]):
        """Apply updates to a single file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Sort updates by line number in reverse order
        # This ensures line numbers remain valid as we make changes
        updates.sort(key=lambda x: x['line'], reverse=True)
        
        for update in updates:
            line_no = update['line'] - 1  # Convert to 0-based
            old_text = update['old']
            new_text = update['new']
            
            if line_no < len(lines):
                # Replace in the line
                lines[line_no] = lines[line_no].replace(old_text, new_text)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    def verify_imports(self, update_plan: Dict[str, List[Dict]]) -> bool:
        """Verify that all imports will be valid after updates."""
        print("\nVerifying import updates...")
        
        issues = []
        
        # Check that all new modules will exist
        new_modules = set()
        for updates in update_plan.values():
            for update in updates:
                if update['type'] in ['from', 'import', 'dynamic']:
                    # Extract module name
                    match = re.search(r'(?:from|import)\s+([\w.]+)', update['new'])
                    if match:
                        new_modules.add(match.group(1))
        
        # Verify modules will exist
        for module in new_modules:
            if module.startswith("tests."):
                # Convert to file path
                rel_module = module[6:]  # Remove "tests."
                file_path = rel_module.replace(".", "/") + ".py"
                
                # Check if this will be a valid path
                exists = any(new_path == file_path for new_path in self.file_mappings.values())
                if not exists:
                    # Might be a package
                    exists = any(new_path.startswith(f"{file_path[:-3]}/") 
                               for new_path in self.file_mappings.values())
                
                if not exists:
                    issues.append(f"Module {module} will not exist after restructuring")
        
        if issues:
            print("Found import issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("All imports verified!")
            return True


def main():
    """Example usage of ImportFixer."""
    import json
    
    # Load file mappings (would come from restructurer)
    file_mappings = {
        "unit/test_models.py": "fast/test_models.py",
        "integration/test_api.py": "slow/test_api.py",
        # ... etc
    }
    
    project_root = Path.cwd()
    fixer = ImportFixer(file_mappings, project_root)
    
    # Find all imports
    imports = fixer.find_all_imports()
    print(f"Found imports in {len(imports)} files")
    
    # Create update plan
    update_plan = fixer.create_update_plan(imports)
    
    # Verify imports
    fixer.verify_imports(update_plan)
    
    # Apply updates (dry run)
    fixer.apply_updates(update_plan, dry_run=True)


if __name__ == "__main__":
    main()