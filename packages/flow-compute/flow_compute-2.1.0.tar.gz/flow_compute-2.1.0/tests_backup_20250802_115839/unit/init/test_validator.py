"""Unit tests for ConfigValidator."""

import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

import httpx

from flow._internal.init.validator import ConfigValidator


class TestConfigValidator(IsolatedAsyncioTestCase):
    """Test configuration validation against API."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = AsyncMock(spec=httpx.AsyncClient)
        self.validator = ConfigValidator(http_client=self.mock_client)

    async def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        config = {"api_key": None}

        result = await self.validator.validate(config)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.projects, [])
        self.assertEqual(result.error_message, "API key is required")

        # Should not make any API calls
        self.mock_client.get.assert_not_called()

    async def test_validate_success(self):
        """Test successful validation."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.test.com"
        }

        # Mock successful responses
        self.mock_client.get.side_effect = [
            AsyncMock(status_code=200),  # /v2/me
            AsyncMock(status_code=200, json=lambda: [
                {"name": "project1", "region": "us-central1-a"},
                {"name": "project2", "region": "eu-west1"}
            ])  # /v2/projects
        ]

        result = await self.validator.validate(config)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.projects), 2)
        self.assertEqual(result.projects[0].name, "project1")
        self.assertEqual(result.projects[0].region, "us-central1-a")
        self.assertIsNone(result.error_message)

        # Verify API calls
        self.assertEqual(self.mock_client.get.call_count, 2)
        calls = self.mock_client.get.call_args_list
        self.assertEqual(calls[0][0][0], "https://api.test.com/v2/me")
        self.assertEqual(calls[1][0][0], "https://api.test.com/v2/projects")

    async def test_validate_invalid_api_key(self):
        """Test validation with invalid API key."""
        config = {
            "api_key": "invalid_key",
            "api_url": "https://api.test.com"
        }

        # Mock 401 response
        self.mock_client.get.side_effect = [
            AsyncMock(status_code=401),  # /v2/me
            AsyncMock(status_code=401)   # /v2/projects
        ]

        result = await self.validator.validate(config)

        self.assertFalse(result.is_valid)
        self.assertEqual(result.projects, [])
        self.assertEqual(result.error_message, "Invalid API key")

    async def test_validate_timeout(self):
        """Test validation with timeout."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.test.com"
        }

        # Mock timeout
        self.mock_client.get.side_effect = asyncio.TimeoutError()

        result = await self.validator.validate(config)

        # Should assume valid to not block user
        self.assertTrue(result.is_valid)
        self.assertEqual(result.projects, [])
        self.assertEqual(result.error_message, "API is slow, continuing without validation")

    async def test_validate_network_error(self):
        """Test validation with network error."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.test.com"
        }

        # Mock network error
        self.mock_client.get.side_effect = httpx.NetworkError("Connection failed")

        result = await self.validator.validate(config)

        # Should assume valid to not block user
        self.assertTrue(result.is_valid)
        self.assertEqual(result.projects, [])
        self.assertEqual(result.error_message, "Cannot reach API, continuing without validation")

    async def test_validate_partial_success(self):
        """Test validation when projects fetch fails but auth succeeds."""
        config = {
            "api_key": "test_key",
            "api_url": "https://api.test.com"
        }

        # Mock mixed responses
        self.mock_client.get.side_effect = [
            AsyncMock(status_code=200),     # /v2/me succeeds
            Exception("Projects API error")  # /v2/projects fails
        ]

        result = await self.validator.validate(config)

        # Should still be valid (auth succeeded)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.projects, [])  # Empty due to error
        self.assertIsNone(result.error_message)

    async def test_client_lifecycle(self):
        """Test that validator manages client lifecycle correctly."""
        # Create validator without client
        validator = ConfigValidator()

        config = {
            "api_key": "test_key",
            "api_url": "https://api.test.com"
        }

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = AsyncMock(status_code=200, json=lambda: [])
            mock_client_class.return_value = mock_client

            result = await validator.validate(config)

            # Should create client
            mock_client_class.assert_called_once_with(timeout=httpx.Timeout(0.5))

            # Should close client
            mock_client.aclose.assert_called_once()
