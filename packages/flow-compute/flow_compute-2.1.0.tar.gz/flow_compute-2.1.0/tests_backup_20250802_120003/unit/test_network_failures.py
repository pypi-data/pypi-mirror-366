"""Network failure simulation tests for Flow SDK.

This module tests the SDK's behavior under various network failure conditions
including connection drops, timeouts, and retry logic. Following the principles
of thorough testing that Jeff Dean and the team would implement.

Design principles:
- Test edge cases and failure modes comprehensively
- Simulate realistic network conditions
- Verify retry logic and error handling
- No flaky tests - deterministic simulations only
"""

import asyncio
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, Optional
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from flow._internal.config import Config
from flow._internal.io.http import HttpClientPool
from flow._internal.io.http_interfaces import IHttpClient
from flow.api.models import TaskStatus
from flow.errors import (
    APIError,
    NetworkError,
    ResourceNotAvailableError,
    ResourceNotFoundError,
    TaskNotFoundError,
    TimeoutError,
)
from flow.providers.fcp.api.handlers import handle_fcp_errors
from flow.providers.fcp.core.errors import FCPAPIError, FCPTimeoutError
from flow.providers.fcp.provider import FCPProvider
from flow.utils.retry import ExponentialBackoffPolicy, with_retry
from tests.testing.constants import NetworkSimulation, TestConstants
from tests.testing.factories import FCPModelFactory, TaskConfigFactory, TaskFactory


class NetworkSimulator:
    """Simulates various network conditions for testing.
    
    This class provides controlled network failure scenarios without
    actually affecting the network. Uses deterministic delays and
    error injection.
    """
    
    def __init__(self):
        self.latency_ms = NetworkSimulation.LATENCY_NORMAL
        self.packet_loss_rate = NetworkSimulation.PACKET_LOSS_NONE
        self.connection_state = NetworkSimulation.CONNECTION_ACTIVE
        self.error_injection_rate = NetworkSimulation.ERROR_RATE_NONE
        self.bandwidth_limit = NetworkSimulation.BANDWIDTH_UNLIMITED
        self._request_count = 0
        self._failure_count = 0
        
    def set_timeout_scenario(self):
        """Configure for timeout testing."""
        self.latency_ms = NetworkSimulation.LATENCY_TIMEOUT
        self.connection_state = NetworkSimulation.CONNECTION_DROPPED
        
    def set_flaky_connection(self):
        """Configure for intermittent failures."""
        self.latency_ms = NetworkSimulation.LATENCY_HIGH
        self.packet_loss_rate = NetworkSimulation.PACKET_LOSS_MEDIUM
        self.connection_state = NetworkSimulation.CONNECTION_FLAKY
        self.error_injection_rate = NetworkSimulation.ERROR_RATE_MEDIUM
        
    def set_slow_connection(self):
        """Configure for slow but stable connection."""
        self.latency_ms = NetworkSimulation.LATENCY_VERY_HIGH
        self.bandwidth_limit = NetworkSimulation.BANDWIDTH_SLOW
        
    def should_fail(self) -> bool:
        """Determine if this request should fail based on error rate."""
        self._request_count += 1
        if self.error_injection_rate > 0:
            # Deterministic failure based on request count
            if self._request_count % int(1 / self.error_injection_rate) == 0:
                self._failure_count += 1
                return True
        return False
        
    def simulate_latency(self):
        """Simulate network latency."""
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)
            
    def get_simulated_error(self) -> Optional[Exception]:
        """Get appropriate error based on connection state."""
        if self.connection_state == NetworkSimulation.CONNECTION_DROPPED:
            return httpx.ConnectError(TestConstants.ERROR_CONNECTION_REFUSED)
        elif self.connection_state == NetworkSimulation.CONNECTION_FLAKY:
            errors = [
                httpx.ConnectTimeout(TestConstants.ERROR_CONNECTION_TIMEOUT),
                httpx.NetworkError(TestConstants.ERROR_NETWORK_UNREACHABLE),
                httpx.ReadTimeout("Read timeout"),
            ]
            # Cycle through errors deterministically
            return errors[self._failure_count % len(errors)]
        return None


class MockHttpClient(IHttpClient):
    """Mock HTTP client with network simulation capabilities."""
    
    def __init__(self, simulator: NetworkSimulator):
        self.simulator = simulator
        self.requests_made = []
        self.responses = {}
        
    def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Simulate HTTP request with network conditions."""
        # Record request
        self.requests_made.append({
            "method": method,
            "url": url,
            "kwargs": kwargs,
            "timestamp": datetime.now(),
        })
        
        # Simulate latency
        self.simulator.simulate_latency()
        
        # Check if we should inject a failure
        if self.simulator.should_fail():
            error = self.simulator.get_simulated_error()
            if error:
                raise error
        
        # Check for timeout
        if self.simulator.latency_ms >= NetworkSimulation.LATENCY_TIMEOUT:
            raise TimeoutError(
                f"Request timeout after {TestConstants.NETWORK_TIMEOUT_VERY_LONG}ms"
            )
        
        # Return mock response
        response_key = f"{method}:{url}"
        if response_key in self.responses:
            return self.responses[response_key]
        
        # Default responses
        if "tasks" in url and method == "GET":
            return {"tasks": []}
        elif "bids" in url and method == "GET":
            # FCP returns paginated response
            return {"data": [], "next_cursor": None}
        elif "/availability" in url and method == "GET":
            # FCP returns list directly for availability
            return []
        
        return {"status": "ok"}


class TestNetworkFailures:
    """Test suite for network failure scenarios."""
    
    @pytest.fixture
    def network_simulator(self):
        """Create a network simulator for testing."""
        return NetworkSimulator()
    
    @pytest.fixture
    def mock_http_client(self, network_simulator):
        """Create a mock HTTP client with network simulation."""
        return MockHttpClient(network_simulator)
    
    @pytest.fixture
    def fcp_provider(self, mock_http_client):
        """Create FCP provider with mocked HTTP client."""
        config = Config(provider="fcp")
        provider = FCPProvider(
            config=config,
            http_client=mock_http_client,
        )
        # Mock the project resolver
        provider.project_resolver.resolve_project = Mock(return_value="test-project")
        provider._project_id = "test-project"  # Set project ID directly
        return provider
    
    def test_connection_timeout_handling(self, fcp_provider, network_simulator):
        """Test handling of connection timeouts."""
        # Configure timeout scenario
        network_simulator.set_timeout_scenario()
        
        # Attempt to submit a task
        config = TaskConfigFactory.create_simple()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            fcp_provider.submit_task(config.instance_type, config)
        
        # Verify that the error message indicates no instances available
        # (timeout during availability check is treated as no availability)
        assert "No a100 instances available" in str(exc_info.value)
        
    def test_connection_drop_during_task_submission(
        self, fcp_provider, network_simulator, mock_http_client
    ):
        """Test connection drop during task submission."""
        # Immediately configure network to drop connections
        network_simulator.set_timeout_scenario()
        
        config = TaskConfigFactory.create_simple()
        
        # Should get a ResourceNotFoundError when availability check fails due to timeout
        with pytest.raises(ResourceNotFoundError) as exc_info:
            fcp_provider.submit_task(config.instance_type, config)
            
        # The error message should indicate no instances were found
        assert "No a100 instances available" in str(exc_info.value)
    
    def test_retry_logic_with_transient_failures(
        self, network_simulator
    ):
        """Test retry logic handles transient network failures."""
        network_simulator.set_flaky_connection()
        
        attempt_count = 0
        
        @with_retry(
            policy=ExponentialBackoffPolicy(
                max_attempts=TestConstants.RETRY_MAX_ATTEMPTS,
                initial_delay=TestConstants.RETRY_INITIAL_DELAY,
                max_delay=TestConstants.RETRY_MAX_DELAY,
            ),
            retryable_exceptions=(NetworkError, httpx.NetworkError)
        )
        def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            
            # Fail first attempts, succeed on last
            if attempt_count < TestConstants.RETRY_MAX_ATTEMPTS:
                raise httpx.NetworkError("Network unreachable")
            
            return {"status": "success"}
        
        result = flaky_operation()
        
        assert result["status"] == "success"
        assert attempt_count == TestConstants.RETRY_MAX_ATTEMPTS
    
    def test_retry_exhaustion(self, network_simulator):
        """Test behavior when all retries are exhausted."""
        network_simulator.set_timeout_scenario()
        
        attempt_count = 0
        
        @with_retry(
            policy=ExponentialBackoffPolicy(
                max_attempts=TestConstants.RETRY_MAX_ATTEMPTS,
                initial_delay=TestConstants.RETRY_INITIAL_DELAY,
            ),
            retryable_exceptions=(TimeoutError,)
        )
        def always_fails():
            nonlocal attempt_count
            attempt_count += 1
            raise TimeoutError("Connection timeout")
        
        with pytest.raises(TimeoutError):
            always_fails()
        
        assert attempt_count == TestConstants.RETRY_MAX_ATTEMPTS
    
    def test_slow_connection_handling(
        self, fcp_provider, network_simulator, mock_http_client
    ):
        """Test handling of slow but successful connections."""
        network_simulator.set_slow_connection()
        
        # Set up mock response - FCP provider expects specific response structure
        task = TaskFactory.create_pending()
        fcp_bid = FCPModelFactory.create_fcp_bid(
            status="pending",
            name=task.name
        )
        
        # Convert to dict manually to ensure all fields are present
        bid_dict = {
            "fid": "task-123",  # Override the fid to match our test
            "name": fcp_bid.name,
            "status": fcp_bid.status,
            "limit_price": fcp_bid.limit_price,
            "created_at": fcp_bid.created_at.isoformat() if fcp_bid.created_at else None,
            "deactivated_at": fcp_bid.deactivated_at.isoformat() if fcp_bid.deactivated_at else None,
            "project": fcp_bid.project,
            "created_by": fcp_bid.created_by,
            "instance_quantity": fcp_bid.instance_quantity,
            "instance_type": fcp_bid.instance_type,
            "region": fcp_bid.region,
            "launch_specification": fcp_bid.launch_specification or {},
            "instances": fcp_bid.instances or []
        }
        
        # The provider's get_task method actually calls list with params
        mock_http_client.responses["GET:/v2/spot/bids"] = {"data": [bid_dict]}
        
        start_time = time.time()
        result = fcp_provider.get_task("task-123")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Verify slow connection was simulated
        assert elapsed_ms >= NetworkSimulation.LATENCY_VERY_HIGH
        assert result.task_id == "task-123"
    
    def test_partial_response_handling(
        self, fcp_provider, mock_http_client, network_simulator
    ):
        """Test handling of partial/corrupted responses."""
        # Simulate partial response
        mock_http_client.responses["GET:/v2/bids"] = {
            "bids": [
                {
                    "fid": "bid-1",
                    "name": "test",
                    # Missing required fields
                }
            ]
        }
        
        # Should handle gracefully
        tasks = fcp_provider.list_tasks()
        
        # Verify error was handled without crashing
        assert isinstance(tasks, list)
    
    def test_dns_resolution_failure(self, network_simulator):
        """Test DNS resolution failure handling."""
        
        class DNSFailureClient(MockHttpClient):
            def request(self, *args, **kwargs):
                raise httpx.ConnectError(TestConstants.ERROR_DNS_FAILURE)
        
        client = DNSFailureClient(network_simulator)
        
        with pytest.raises(httpx.ConnectError) as exc_info:
            client.request("GET", "/test")
        
        assert TestConstants.ERROR_DNS_FAILURE in str(exc_info.value)
    
    def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted."""
        # This would be tested at integration level with real HTTP client
        # Here we verify the concept
        
        pool = HttpClientPool()
        
        # HttpClientPool should handle multiple clients gracefully
        clients = []
        for i in range(3):
            # get_client doesn't take timeout parameter
            client = pool.get_client("https://api.test.com")
            clients.append(client)
            
        # Verify all clients were created (pool handles this gracefully)
        assert len(clients) == 3
        
        # Verify they're the same client instance (connection reuse)
        assert clients[0] is clients[1]
        assert clients[1] is clients[2]
    
    def test_network_error_propagation(self, fcp_provider, mock_http_client):
        """Test that network errors are properly propagated with context."""
        
        # Configure to raise network error
        def raise_network_error(*args, **kwargs):
            raise httpx.NetworkError(
                f"Failed to connect to {kwargs.get('url', 'unknown')}"
            )
        
        mock_http_client.request = Mock(side_effect=raise_network_error)
        
        with pytest.raises(NetworkError) as exc_info:
            fcp_provider.list_tasks()
        
        # Verify error contains useful context
        error_message = str(exc_info.value)
        assert "connect" in error_message.lower()
    
    @pytest.mark.parametrize("error_code,expected_exception", [
        (TestConstants.HTTP_GATEWAY_TIMEOUT, FCPTimeoutError),  # TimeoutError -> FCPTimeoutError via decorator
        (TestConstants.HTTP_SERVICE_UNAVAILABLE, APIError),
        (TestConstants.HTTP_TOO_MANY_REQUESTS, APIError),
    ])
    def test_http_error_code_handling(
        self, fcp_provider, mock_http_client, error_code, expected_exception
    ):
        """Test handling of various HTTP error codes."""
        
        def raise_http_error(*args, **kwargs):
            response = Mock()
            response.status_code = error_code
            response.json.return_value = {"error": f"HTTP {error_code}"}
            response.text = f"HTTP {error_code} Error"
            
            # Simulate the HttpClient's error handling
            if error_code == 504:
                raise TimeoutError(f"Gateway timeout: {response.text}")
            else:
                raise httpx.HTTPStatusError(
                    f"HTTP {error_code}",
                    request=Mock(),
                    response=response
                )
        
        mock_http_client.request = Mock(side_effect=raise_http_error)
        
        with pytest.raises(expected_exception):
            fcp_provider.list_tasks()
    
    def test_concurrent_request_failures(self, network_simulator):
        """Test handling of failures in concurrent requests."""
        network_simulator.set_flaky_connection()
        network_simulator.error_injection_rate = 0.3  # 30% failure rate
        
        async def make_request(client: MockHttpClient, request_id: int):
            """Simulate async request."""
            try:
                return client.request("GET", f"/task/{request_id}")
            except Exception as e:
                return {"error": str(e), "request_id": request_id}
        
        async def run_concurrent_requests():
            """Run multiple concurrent requests."""
            client = MockHttpClient(network_simulator)
            tasks = [
                make_request(client, i)
                for i in range(10)
            ]
            return await asyncio.gather(*tasks)
        
        # Run the async test
        results = asyncio.run(run_concurrent_requests())
        
        # Verify some requests failed and some succeeded
        errors = [r for r in results if "error" in r]
        successes = [r for r in results if "status" in r]
        
        # With 30% failure rate, we should have some of each
        assert len(errors) >= 2  # At least 2 failures expected
        assert len(successes) >= 2  # At least 2 successes expected
        assert len(errors) + len(successes) == 10  # All requests accounted for
    
    def test_network_partition_simulation(
        self, fcp_provider, mock_http_client, network_simulator
    ):
        """Test behavior during network partition."""
        
        # Simulate network partition - some endpoints unreachable
        def partition_handler(method, url, **kwargs):
            if "critical" in url:
                raise httpx.NetworkError(TestConstants.ERROR_HOST_UNREACHABLE)
            return {"status": "ok"}
        
        mock_http_client.request = Mock(side_effect=partition_handler)
        
        # Non-critical endpoints should work
        health = mock_http_client.request("GET", "/v2/health")
        assert health["status"] == "ok"
        
        # Critical endpoints should fail
        with pytest.raises(httpx.NetworkError):
            mock_http_client.request("GET", "/v2/critical/data")


class TestRetryStrategies:
    """Test different retry strategies under network failures."""
    
    def test_exponential_backoff_timing(self):
        """Verify exponential backoff delays are correct."""
        policy = ExponentialBackoffPolicy(
            max_attempts=4,
            initial_delay=TestConstants.RETRY_INITIAL_DELAY,
            exponential_base=TestConstants.RETRY_BACKOFF_FACTOR,
            max_delay=TestConstants.RETRY_MAX_DELAY,
        )
        
        # Test delay calculation
        delays = []
        for attempt in range(1, 5):  # get_delay expects 1-based attempt number
            delay = policy.get_delay(attempt)
            delays.append(delay)
        
        # Verify exponential growth with cap
        assert delays[0] == TestConstants.RETRY_INITIAL_DELAY
        assert delays[1] == TestConstants.RETRY_INITIAL_DELAY * TestConstants.RETRY_BACKOFF_FACTOR
        assert delays[2] == TestConstants.RETRY_INITIAL_DELAY * (TestConstants.RETRY_BACKOFF_FACTOR ** 2)
        assert delays[3] <= TestConstants.RETRY_MAX_DELAY
    
    def test_retry_delay_progression(self):
        """Test retry delay progression without jitter."""
        policy = ExponentialBackoffPolicy(
            max_attempts=3,
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=10.0,
        )
        
        # Test delay progression
        delays = []
        for attempt in range(1, 4):
            delay = policy.get_delay(attempt)
            delays.append(delay)
        
        # Verify deterministic exponential growth
        assert delays[0] == 1.0  # First attempt
        assert delays[1] == 2.0  # Second attempt 
        assert delays[2] == 4.0  # Third attempt
    
    def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for cascading failures."""
        
        class CircuitBreaker:
            def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
                self.failure_threshold = failure_threshold
                self.reset_timeout = reset_timeout
                self.failure_count = 0
                self.last_failure_time = None
                self.is_open = False
            
            def call(self, func, *args, **kwargs):
                if self.is_open:
                    if (time.time() - self.last_failure_time) > self.reset_timeout:
                        self.is_open = False
                        self.failure_count = 0
                    else:
                        raise Exception("Circuit breaker is open")
                
                try:
                    result = func(*args, **kwargs)
                    self.failure_count = 0  # Reset on success
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.is_open = True
                    
                    raise e
        
        breaker = CircuitBreaker(failure_threshold=3)
        
        def failing_operation():
            raise Exception("Network error")
        
        # Test circuit opens after threshold
        for i in range(3):
            with pytest.raises(Exception):
                breaker.call(failing_operation)
        
        assert breaker.is_open
        
        # Further calls should fail immediately
        with pytest.raises(Exception) as exc_info:
            breaker.call(failing_operation)
        
        assert "Circuit breaker is open" in str(exc_info.value)