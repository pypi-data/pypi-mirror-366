# Flow SDK Test Suite

This directory contains the comprehensive test suite for the Flow SDK.

## Directory Structure

```
tests/
├── smoke/           # Basic smoke tests for quick validation
├── unit/            # Unit tests for individual components
├── integration/     # Integration tests for component interactions
├── e2e/             # End-to-end tests for complete workflows
├── functional/      # Functional tests for specific features
├── performance/     # Performance benchmarks and regression tests
├── fixtures/        # Test fixtures and mock data
├── utils/           # Test utilities and helpers
├── testing/         # Test framework and base classes
├── scripts/         # Test runner scripts and tools
├── tools/           # Specialized test tools and validators
├── config/          # Test configuration files
├── docs/            # Test documentation
├── data/            # Test data files
├── analysis/        # Test analysis and reporting
└── verification/    # Verification scripts for deployments
```

## Test Categories

### Smoke Tests (`smoke/`)
- Quick validation tests that run in seconds
- Basic import and functionality checks
- Used for rapid feedback during development

### Unit Tests (`unit/`)
- Isolated tests for individual classes and functions
- Mock external dependencies
- Fast execution, comprehensive coverage

### Integration Tests (`integration/`)
- Test interactions between components
- May use real services with test configurations
- Validate API contracts and data flow

### End-to-End Tests (`e2e/`)
- Complete workflow tests
- Test real-world scenarios
- May require external services

### Functional Tests (`functional/`)
- Feature-specific tests
- Test business logic and user scenarios
- Include example validation and specialized features

### Performance Tests (`performance/`)
- Benchmark critical operations
- Track performance regressions
- Memory and resource usage tests

## Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=flow tests/

# Run specific test file
pytest tests/unit/test_models.py

# Run tests matching pattern
pytest -k "gpu" tests/
```

## Test Scripts

- `scripts/run_tests.py` - Main test runner with environment setup
- `scripts/run_ssh_tests.py` - Specialized SSH test runner
- `scripts/validate_examples.py` - Validate example code

## Configuration

Test configurations are stored in `config/`:
- `mock_flow_config.yaml` - Mock Flow configuration
- `requirements-mock.txt` - Test dependencies

## Documentation

Additional test documentation in `docs/`:
- Original test documentation
- Mock API server documentation
- Test fixes and improvements summary