# Flow SDK Test Suite

This document provides a comprehensive guide to the Flow SDK test suite, helping developers understand the testing strategy, run tests effectively, and contribute new tests.

## Table of Contents

- [Test Organization](#test-organization)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Infrastructure](#test-infrastructure)
- [Performance Testing](#performance-testing)
- [Best Practices](#best-practices)

## Test Organization

The test suite is organized into several directories, each serving a specific purpose:

```
tests/
├── unit/               # Unit tests for individual components
├── integration/        # Integration tests with real or simulated services
├── e2e/               # End-to-end tests for complete workflows
├── performance/       # Performance benchmarks and regression tests
├── analysis/          # Test analysis tools and reports
├── testing/           # Shared test utilities and fixtures
└── utils/             # Test helper utilities
```

### Directory Structure

- **unit/**: Tests individual functions and classes in isolation
- **integration/**: Tests component interactions with external services
- **e2e/**: Tests complete user workflows from CLI to task completion
- **performance/**: Benchmarks critical operations and tracks regressions
- **analysis/**: Tools for analyzing test coverage and dependencies
- **testing/**: Shared fixtures, builders, and test constants
- **utils/**: Helper utilities like mock SSH servers

## Test Categories

### Unit Tests

Unit tests verify individual components work correctly in isolation:

- **Provider Tests**: Test provider implementations (FCP, Local, etc.)
- **Model Tests**: Validate data models and serialization
- **CLI Tests**: Test command parsing and execution
- **Utility Tests**: Test helper functions and utilities

Example:
```python
class TestTaskModel:
    """Test Task model functionality."""
    
    def test_task_creation(self):
        """Test creating a task with required fields."""
        task = Task(
            task_id="test-123",
            name="test",
            status=TaskStatus.RUNNING,
            # ... other fields
        )
        assert task.task_id == "test-123"
```

### Integration Tests

Integration tests verify components work together correctly:

- **API Integration**: Test real API interactions
- **Storage Integration**: Test file share and volume operations
- **SSH Integration**: Test SSH connectivity and tunneling
- **Docker Integration**: Test container management

Example:
```python
class TestFCPIntegration:
    """Test real integration with FCP API."""
    
    @pytest.mark.integration
    async def test_submit_task(self, fcp_provider):
        """Test submitting a real task to FCP."""
        task = await fcp_provider.submit_task(config)
        assert task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]
```

### End-to-End Tests

E2E tests verify complete user workflows:

- **CLI Workflows**: Test complete CLI command sequences
- **Task Lifecycle**: Test task submission through completion
- **Multi-Node**: Test distributed computing scenarios

Example:
```python
class TestEndToEndWorkflows:
    """Test complete workflows with real infrastructure."""
    
    def test_submit_and_monitor_task(self):
        """Test submitting a task and monitoring its progress."""
        # Submit task via CLI
        result = run_cli(["flow", "submit", "script.py"])
        task_id = extract_task_id(result.output)
        
        # Monitor until completion
        wait_for_task_completion(task_id)
```

### Performance Tests

Performance tests track execution speed and resource usage:

- **Benchmarks**: Measure operation performance
- **Regression Tracking**: Compare against baselines
- **Scalability Tests**: Test with large datasets

Example:
```python
class TestPerformanceRegression:
    """Test suite for tracking performance regressions."""
    
    def test_task_list_performance(self, tracker):
        """Measure task list filtering performance."""
        with tracker.measure("task_filter_complex"):
            filtered = [t for t in tasks if complex_filter(t)]
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::TestTaskModel::test_task_creation
```

### Test Markers

Tests are marked for selective execution:

```bash
# Run only fast tests
pytest -m "not slow"

# Run integration tests
pytest -m integration

# Run tests requiring Docker
pytest -m docker

# Skip tests requiring real API
pytest -m "not requires_api"
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=flow --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Performance Testing

```bash
# Run performance tests
pytest tests/performance/

# Update performance baselines
python tests/performance/test_regression_tracking.py --update-baselines
```

## Writing Tests

### Test Structure

Follow this structure for consistency:

```python
"""Module docstring explaining test purpose."""

import pytest
from flow.module import Component


class TestComponent:
    """Test class docstring explaining scope."""
    
    @pytest.fixture
    def component(self):
        """Create component instance for testing."""
        return Component()
    
    def test_basic_functionality(self, component):
        """Test method docstring explaining what is tested."""
        result = component.method()
        assert result == expected
    
    @pytest.mark.parametrize("input,expected", [
        ("value1", "result1"),
        ("value2", "result2"),
    ])
    def test_various_inputs(self, component, input, expected):
        """Test with multiple input scenarios."""
        assert component.process(input) == expected
```

### Using Test Builders

Use builders for complex test data:

```python
from tests.testing import TaskBuilder, TaskConfigBuilder

def test_with_builders():
    """Test using builder pattern."""
    # Create task with builder
    task = (TaskBuilder()
            .with_status(TaskStatus.RUNNING)
            .with_gpu("a100", count=2)
            .build())
    
    # Create config with builder
    config = (TaskConfigBuilder()
             .with_instance_type("gpu.a100")
             .with_env({"KEY": "value"})
             .build())
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

def test_with_mocks():
    """Test with mocked external service."""
    mock_api = Mock()
    mock_api.submit_task.return_value = {"task_id": "123"}
    
    with patch('flow.api.client', mock_api):
        result = submit_task(config)
        assert result.task_id == "123"
```

## Test Infrastructure

### Shared Fixtures

Common fixtures are defined in `conftest.py` files:

- `tmp_path`: Temporary directory for test files
- `mock_http_client`: Mocked HTTP client
- `fcp_provider`: Configured FCP provider instance
- `test_config`: Standard test configuration

### Test Constants

Use centralized constants from `tests/testing/constants.py`:

```python
from tests.testing.constants import TestConstants

def test_with_constants():
    """Use standardized test data."""
    task_id = TestConstants.TASK_IDS.STANDARD
    instance = TestConstants.INSTANCES.GPU_A100
```

### Test Utilities

Helper utilities in `tests/testing/`:

- **builders.py**: Builder classes for test data
- **mocks.py**: Reusable mock objects
- **fixtures.py**: Shared pytest fixtures
- **matchers.py**: Custom assertion helpers

## Performance Testing

### Running Benchmarks

```bash
# Run all benchmarks
pytest tests/performance/ -v

# Run specific benchmark
pytest tests/performance/test_benchmarks.py::TestModelPerformance
```

### Regression Detection

The test suite automatically detects performance regressions:

1. Baselines are stored in `tests/performance/.baselines.json`
2. Tests measure current performance
3. Comparisons flag regressions > 20%
4. Reports show performance trends

### Updating Baselines

When performance legitimately improves:

```bash
# Update baselines after confirming improvements
python tests/performance/test_regression_tracking.py --update-baselines
```

## Best Practices

### 1. Test Isolation

- Tests should not depend on each other
- Clean up resources in teardown
- Use fixtures for setup/teardown

### 2. Clear Test Names

- Test names should describe what is being tested
- Use descriptive assertions with clear messages
- Include docstrings explaining test purpose

### 3. Appropriate Test Levels

- Unit tests for logic and calculations
- Integration tests for external interactions
- E2E tests for critical user workflows

### 4. Mock External Dependencies

- Mock API calls in unit tests
- Use real services only in integration tests
- Provide clear skip messages when services unavailable

### 5. Test Edge Cases

- Test error conditions
- Test boundary values
- Test concurrent operations
- Test clock skew scenarios

### 6. Performance Awareness

- Keep unit tests fast (< 100ms)
- Mark slow tests appropriately
- Use performance tracking for critical paths

### 7. Maintainable Tests

- Avoid complex test logic
- Use builders for test data
- Extract common patterns to helpers
- Keep tests focused on one aspect

## Contributing Tests

When adding new tests:

1. **Choose the right category**: Unit, integration, or E2E
2. **Follow naming conventions**: `test_<feature>_<aspect>.py`
3. **Add appropriate markers**: `@pytest.mark.slow`, `@pytest.mark.integration`
4. **Include docstrings**: Explain what the test verifies
5. **Use existing patterns**: Follow established test patterns
6. **Consider performance**: Add benchmarks for critical paths

## Troubleshooting

### Common Issues

**Tests failing locally but passing in CI:**
- Check for environment dependencies
- Verify timezone and locale settings
- Ensure clean test environment

**Flaky tests:**
- Add retries for network operations
- Use appropriate timeouts
- Mock time-sensitive operations

**Performance test failures:**
- Check system load
- Run in isolated environment
- Update baselines if legitimate

### Debug Options

```bash
# Run with verbose output
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Run specific test with full traceback
pytest tests/unit/test_models.py::test_name --tb=long
```

## Continuous Integration

Tests run automatically on:

- Pull requests: Unit and integration tests
- Main branch: Full test suite including E2E
- Nightly: Extended test suite with performance

See `.github/workflows/` for CI configuration.