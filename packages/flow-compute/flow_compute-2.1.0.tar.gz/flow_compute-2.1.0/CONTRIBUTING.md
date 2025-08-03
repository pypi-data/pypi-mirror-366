# Contributing to Flow SDK

## Development Setup

```bash
# Clone the repository
git clone https://github.com/mlfoundry/flow-sdk.git
cd flow-sdk

# Install dependencies
uv sync --dev

# Configure API key
uv run flow init

# Run tests
uv run pytest

# Run examples
uv run python examples/01_basics/hello_gpu.py
```

## Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_models.py

# Run with coverage
uv run pytest --cov=flow
```

## Code Style

```bash
# Format code
uv run black src/flow tests

# Lint
uv run ruff check src/flow tests

# Type check
uv run mypy src/flow
```