# Test Restructuring - Detailed Implementation Plan

## Phase 1: Analysis and Preparation (Tasks 1-5)

### 1.1 Document Current Structure
- [ ] Count total test files in each directory
- [ ] List all test categories and their purposes
- [ ] Document special test types (fixtures, mocks, etc.)
- [ ] Note any custom test infrastructure

### 1.2 Create File Mapping
```python
# Example mapping structure
FILE_MAPPING = {
    "tests/unit/test_models.py": "tests/fast/test_models.py",
    "tests/integration/test_fcp_integration.py": "tests/slow/providers/test_fcp_integration.py",
    "tests/e2e/test_gpu.py": "tests/slow/e2e/test_gpu.py",
    # ... complete mapping for all ~200 files
}
```

### 1.3 Import Dependency Analysis
- [ ] Scan all .py files for `from tests.` imports
- [ ] Scan all .py files for `import tests.` statements
- [ ] Find relative imports within test files (`from ..fixtures`)
- [ ] Identify external references to test utilities
- [ ] Create dependency graph

### 1.4 Performance Analysis
- [ ] Run pytest with `--durations=0` to get all test times
- [ ] Categorize tests by execution time:
  - Fast: <1 second
  - Slow: ≥1 second
- [ ] Mark tests that require external services
- [ ] Identify tests with `@pytest.mark.slow` or similar

### 1.5 Create Backup
```bash
cp -r tests tests_backup_$(date +%Y%m%d_%H%M%S)
```

## Phase 2: Structure Creation (Task 6)

### 2.1 New Directory Structure
```bash
mkdir -p tests/fast
mkdir -p tests/slow/{providers,e2e,system}
mkdir -p tests/support/{fixtures,mocks,utils,data,scripts}
```

### 2.2 Create __init__.py Files
```bash
touch tests/fast/__init__.py
touch tests/slow/__init__.py
touch tests/slow/providers/__init__.py
touch tests/slow/e2e/__init__.py
touch tests/slow/system/__init__.py
touch tests/support/__init__.py
# ... etc for all subdirectories
```

## Phase 3: File Migration (Tasks 7-9)

### 3.1 Move Fast Tests (Unit Tests)
```python
# Criteria: <1s, mocked dependencies, no external services
FAST_TESTS = [
    "tests/unit/test_models.py",
    "tests/unit/test_errors.py",
    "tests/unit/test_config.py",
    "tests/smoke/test_basic.py",
    # ... complete list
]
```

### 3.2 Move Slow Tests (Integration/E2E)
```python
# Criteria: ≥1s, real dependencies, external services
SLOW_TESTS = [
    "tests/integration/**/*.py",
    "tests/e2e/**/*.py",
    "tests/functional/test_*_integration.py",
    # ... complete list
]
```

### 3.3 Consolidate Support Files
```python
SUPPORT_MAPPING = {
    "tests/fixtures/": "tests/support/fixtures/",
    "tests/utils/": "tests/support/utils/",
    "tests/testing/": "tests/support/framework/",
    "tests/data/": "tests/support/data/",
    "tests/config/": "tests/support/config/",
    "tests/scripts/": "tests/support/scripts/",
    "tests/tools/": "tests/support/tools/",
    "tests/docs/": "tests/support/docs/",
}
```

## Phase 4: Import Updates (Tasks 10-11)

### 4.1 Update Test File Imports
```python
# Old: from tests.fixtures.api_responses import mock_task
# New: from tests.support.fixtures.api_responses import mock_task

# Old: from ..testing.base import BaseTest
# New: from tests.support.framework.base import BaseTest

# Old: from tests.unit.test_models import create_task
# New: from tests.fast.test_models import create_task
```

### 4.2 Update Source Code Test References
```python
# Files to check:
# - src/**/*.py for any test imports
# - setup.py/pyproject.toml for test dependencies
# - Any scripts that import test utilities
```

### 4.3 Import Update Script
```python
import re
import os

def update_imports(file_path, import_mapping):
    with open(file_path, 'r') as f:
        content = f.read()
    
    for old_import, new_import in import_mapping.items():
        # Handle: from tests.X import Y
        content = re.sub(
            rf'from {re.escape(old_import)} import',
            f'from {new_import} import',
            content
        )
        # Handle: import tests.X
        content = re.sub(
            rf'import {re.escape(old_import)}',
            f'import {new_import}',
            content
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
```

## Phase 5: Configuration Updates (Tasks 12-15)

### 5.1 Update pytest.ini
```ini
[tool:pytest]
testpaths = tests/fast tests/slow
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    fast: marks tests as fast (<1s)
    slow: marks tests as slow (≥1s)
    unit: unit tests (deprecated, use fast)
    integration: integration tests (deprecated, use slow)
```

### 5.2 Update conftest.py
```python
# Update fixture paths
# Update test categorization logic
# Update any path-dependent fixtures
```

### 5.3 Path Reference Updates
- [ ] Update `__file__` based paths
- [ ] Fix relative path references
- [ ] Update test data loading paths
- [ ] Fix mock config file paths

### 5.4 CI/CD Configuration
```yaml
# GitHub Actions example
- name: Run fast tests
  run: pytest tests/fast -v

- name: Run slow tests
  run: pytest tests/slow -v -m "not gpu"
```

## Phase 6: Consolidation (Tasks 16-18)

### 6.1 Remove Duplicate Files
```python
DUPLICATES_TO_CONSOLIDATE = [
    ("test_fcp_integration.py", "test_fcp_integration_fixed.py"),
    ("test_fcp_user_journeys.py", "test_fcp_user_journeys_improved.py"),
    # ... identify all _fixed, _updated variants
]
```

### 6.2 Update Test Runners
- [ ] Update `tests/support/scripts/run_tests.py` paths
- [ ] Fix test discovery logic
- [ ] Update coverage configuration

## Phase 7: Verification (Tasks 19-22)

### 7.1 Test Execution Verification
```bash
# Run all tests
pytest tests/ -v

# Run fast tests only
pytest tests/fast -v

# Run slow tests only  
pytest tests/slow -v

# Check coverage
pytest tests/ --cov=flow --cov-report=html
```

### 7.2 Import Verification Script
```python
def verify_no_broken_imports():
    """Scan all Python files for broken imports."""
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                try:
                    compile(open(file).read(), file, 'exec')
                except SyntaxError as e:
                    print(f"Syntax error in {file}: {e}")
```

### 7.3 Documentation Updates
- [ ] Update tests/README.md
- [ ] Update contributing guidelines
- [ ] Update developer documentation
- [ ] Create migration guide

### 7.4 Cleanup
- [ ] Remove empty directories
- [ ] Delete backup if successful
- [ ] Update .gitignore if needed

## Rollback Plan

If issues arise:
```bash
# Restore from backup
rm -rf tests
mv tests_backup_[timestamp] tests
```

## Success Criteria

1. All tests pass with new structure
2. No broken imports in any Python files
3. CI/CD pipeline works with new paths
4. Test execution time clearly separated (fast <1s, slow ≥1s)
5. Documentation accurately reflects new structure
6. No duplicate test files remain