"""Minimal configuration for e2e tests."""

import pytest


def pytest_addoption(parser):
    """Add --run-e2e flag."""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run e2e tests against real API"
    )


def pytest_collection_modifyitems(config, items):
    """Skip e2e tests unless --run-e2e is passed."""
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="use --run-e2e to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)
