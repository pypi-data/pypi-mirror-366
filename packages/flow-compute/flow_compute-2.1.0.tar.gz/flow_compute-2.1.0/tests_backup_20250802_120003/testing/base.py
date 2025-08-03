"""Base test classes for integration testing."""

import logging

import pytest

from flow import Flow
from flow._internal.config import Config
from flow.providers.fcp.provider import FCPProvider

from .api_state import check_api_health

logger = logging.getLogger(__name__)


class IntegrationTest:
    """Base class for integration tests.
    
    Provides:
    - Automatic API health checks
    - Proper provider initialization
    - Clear skip reasons for API issues
    """

    @pytest.fixture(autouse=True)
    def check_api_state(self, request):
        """Check API state before each test.
        
        This fixture runs automatically and skips tests if the API
        is in a bad state (quota exceeded, no instances, etc).
        """
        # Skip this check for unit tests
        if "unit" in str(request.fspath):
            return

        # Get API key from environment
        api_key = os.environ.get("FCP_TEST_API_KEY")
        if not api_key:
            pytest.skip("FCP_TEST_API_KEY not set")

        # Create temporary provider to check health
        config = Config(
            provider="fcp",
            auth_token=api_key,
            provider_config={
                "api_url": os.environ.get("FCP_TEST_API_URL", "https://api.mlfoundry.com"),
                "project": os.environ.get("FCP_TEST_PROJECT", "test"),
                "region": None  # Don't specify region for health check
            }
        )

        provider = FCPProvider.from_config(config)
        health = check_api_health(provider)

        if not health.can_run_tests:
            pytest.skip(health.skip_reason)

        # Store health info for tests that need it
        self._api_health = health

    @pytest.fixture
    def flow(self):
        """Create Flow instance with test credentials.
        
        This fixture creates a properly configured Flow instance
        and ensures the API is healthy before returning it.
        """
        api_key = os.environ.get("FCP_TEST_API_KEY")
        if not api_key:
            pytest.skip("FCP_TEST_API_KEY not set")

        config = Config(
            provider="fcp",
            auth_token=api_key,
            provider_config={
                "api_url": os.environ.get("FCP_TEST_API_URL", "https://api.mlfoundry.com"),
                "project": os.environ.get("FCP_TEST_PROJECT", "test"),
                "region": None  # Let provider find best region
            }
        )

        return Flow(config=config)

    @pytest.fixture
    def available_instance(self, flow):
        """Get an available instance type for testing.
        
        This fixture provides a valid instance type that can be used
        in tests, based on what's actually available in the API.
        """
        if hasattr(self, '_api_health') and self._api_health.available_instances:
            # Use cheapest available instance
            instances = sorted(
                self._api_health.available_instances,
                key=lambda x: x.price_per_hour
            )
            return instances[0].instance_type

        # Fallback to discovery
        provider = flow._ensure_provider()
        instances = provider.find_instances({"max_price_per_hour": 10.0}, limit=1)
        if not instances:
            pytest.skip("No instances available for testing")

        return instances[0].instance_type


import os  # Add missing import
