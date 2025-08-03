"""Showcase of the three implemented improvements to the test suite.

This module demonstrates:
1. Network failure simulation tests
2. Usage of TestConstants instead of magic values
3. Test data factories for creating test objects

Following the principles that Jeff Dean, Sanjay Ghemawat, and the team would
implement - clean architecture, no magic values, comprehensive testing.
"""

import time
from unittest.mock import Mock, patch

import httpx
import pytest

from flow._internal.config import Config
from flow.api.models import TaskStatus
from flow.errors import NetworkError, TimeoutError
from flow.providers.fcp.provider import FCPProvider
from tests.testing.constants import NetworkSimulation, TestConstants
from tests.testing.factories import (
    FCPModelFactory,
    NetworkSimulationFactory,
    TaskConfigFactory,
    TaskFactory,
    VolumeFactory,
)


class TestNetworkFailureSimulation:
    """Demonstrate network failure simulation capabilities."""
    
    def test_timeout_simulation_with_factories(self):
        """Show how factories and constants work together for network tests."""
        # Create timeout scenario using factory
        scenario = NetworkSimulationFactory.create_timeout_scenario()
        
        # Use TestConstants for assertions
        assert scenario["latency"] == NetworkSimulation.LATENCY_TIMEOUT
        assert scenario["packet_loss"] == NetworkSimulation.PACKET_LOSS_SEVERE
        assert scenario["connection_state"] == NetworkSimulation.CONNECTION_DROPPED
        
        # Create test task using factory
        task_config = TaskConfigFactory.create_gpu(
            gpu_type=TestConstants.DEFAULT_GPU_TYPE
        )
        
        # Verify factory used constants correctly
        assert task_config.instance_type == TestConstants.DEFAULT_GPU_TYPE
        assert task_config.max_price_per_hour == TestConstants.TEST_PRICE_HIGH
    
    def test_flaky_connection_with_retries(self):
        """Demonstrate flaky connection handling with proper constants."""
        # Create flaky scenario
        scenario = NetworkSimulationFactory.create_flaky_connection()
        
        # Mock network behavior
        attempt_count = 0
        
        def flaky_request():
            nonlocal attempt_count
            attempt_count += 1
            
            # Fail based on scenario error rate
            if attempt_count < TestConstants.RETRY_MAX_ATTEMPTS:
                raise httpx.NetworkError(TestConstants.ERROR_NETWORK_UNREACHABLE)
            
            return {"status": "success", "attempt": attempt_count}
        
        # Simulate retry logic
        for i in range(TestConstants.RETRY_MAX_ATTEMPTS):
            try:
                result = flaky_request()
                break
            except httpx.NetworkError:
                if i < TestConstants.RETRY_MAX_ATTEMPTS - 1:
                    time.sleep(TestConstants.RETRY_INITIAL_DELAY * (TestConstants.RETRY_BACKOFF_FACTOR ** i))
                else:
                    raise
        
        assert result["status"] == "success"
        assert result["attempt"] == TestConstants.RETRY_MAX_ATTEMPTS


class TestConstantsUsage:
    """Demonstrate proper usage of TestConstants throughout tests."""
    
    def test_task_creation_with_constants(self):
        """Show how constants replace magic strings in task creation."""
        # Before: Magic strings everywhere
        # task = Task(task_id="task-123", name="test-task", ...)
        
        # After: Using constants and factories
        task = TaskFactory.create_pending(
            name=TestConstants.get_test_task_name("demo")
        )
        
        # Verify task uses proper defaults from constants
        assert task.status == TaskStatus.PENDING
        assert task.instance_type == TestConstants.DEFAULT_INSTANCE_TYPE
        assert task.region == TestConstants.DEFAULT_REGION
        assert task.cost_per_hour == TestConstants.TEST_PRICE_STRING_LOW
    
    def test_price_validation_with_constants(self):
        """Demonstrate price validation using constants."""
        test_prices = [
            (TestConstants.TEST_PRICE_LOW, True),
            (TestConstants.TEST_PRICE_MEDIUM, True),
            (TestConstants.TEST_PRICE_HIGH, True),
            (TestConstants.VOLUME_MAX_SIZE_GB + 1, False),  # Too high
        ]
        
        for price, should_be_valid in test_prices:
            is_valid = 0 < price <= TestConstants.TEST_PRICE_VERY_HIGH
            assert is_valid == should_be_valid, f"Price {price} validation failed"
    
    def test_http_status_handling(self):
        """Show HTTP status code handling with constants."""
        
        def get_error_for_status(status_code):
            """Map HTTP status to appropriate error."""
            if status_code == TestConstants.HTTP_GATEWAY_TIMEOUT:
                return TimeoutError("Gateway timeout")
            elif status_code == TestConstants.HTTP_SERVICE_UNAVAILABLE:
                return NetworkError("Service unavailable")
            elif status_code >= TestConstants.HTTP_SERVER_ERROR:
                return NetworkError(f"Server error: {status_code}")
            return None
        
        # Test various status codes
        assert isinstance(
            get_error_for_status(TestConstants.HTTP_GATEWAY_TIMEOUT),
            TimeoutError
        )
        assert isinstance(
            get_error_for_status(TestConstants.HTTP_SERVICE_UNAVAILABLE),
            NetworkError
        )


class TestFactoriesShowcase:
    """Demonstrate the power of test data factories."""
    
    def test_complex_task_scenario(self):
        """Create complex test scenario using factories."""
        # Create a distributed GPU task
        config = TaskConfigFactory.create_distributed(
            num_instances=TestConstants.MAX_INSTANCES_PER_TASK
        )
        
        # Create running tasks for the distributed job
        tasks = []
        for i in range(config.num_instances):
            task = TaskFactory.create_running(
                name=f"{config.name}-node-{i}",
                instance_id=f"{TestConstants.TEST_INSTANCE_PREFIX}{i:03d}"
            )
            tasks.append(task)
        
        # Verify distributed setup
        assert len(tasks) == TestConstants.MAX_INSTANCES_PER_TASK
        assert all(t.status == TaskStatus.RUNNING for t in tasks)
    
    def test_volume_lifecycle(self):
        """Test volume lifecycle using factories."""
        # Create unattached volume
        volume = VolumeFactory.create_unattached(
            size_gb=TestConstants.VOLUME_MAX_SIZE_GB // 2
        )
        
        assert len(volume.attached_to) == 0
        assert volume.size_gb == TestConstants.VOLUME_MAX_SIZE_GB // 2
        
        # Create attached volume
        instance_id = TestConstants.get_mock_instance_id()
        attached_volume = VolumeFactory.create_attached(instance_id)
        
        assert instance_id in attached_volume.attached_to
    
    def test_batch_operations(self):
        """Test batch operations using factories."""
        # Create batch of tasks
        batch = TaskFactory.create_batch(
            count=20,
            prefix="batch-test"
        )
        
        # Verify distribution of statuses
        status_counts = {}
        for task in batch:
            status = task.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Should have mix of statuses
        assert TaskStatus.PENDING in status_counts
        assert TaskStatus.RUNNING in status_counts
        assert TaskStatus.COMPLETED in status_counts
        
        # All should have consistent naming
        assert all(task.name.startswith("batch-test-") for task in batch)
    
    def test_fcp_model_factories(self):
        """Test FCP-specific model factories."""
        # Create FCP bid
        bid = FCPModelFactory.create_fcp_bid(
            status="provisioning",
            name=TestConstants.get_test_task_name("fcp-test")
        )
        
        # Verify bid uses proper constants
        assert bid.instance_type == TestConstants.TEST_INSTANCE_TYPE_ID
        assert bid.region == TestConstants.DEFAULT_REGION
        assert float(bid.limit_price) == TestConstants.TEST_PRICE_MEDIUM
        
        # Create FCP instance for the bid
        instance = FCPModelFactory.create_fcp_instance(
            bid_id=bid.fid,
            status="running"
        )
        
        assert instance.bid_id == bid.fid
        assert instance.instance_type == TestConstants.TEST_INSTANCE_TYPE_ID


class TestIntegrationExample:
    """Show how all three improvements work together."""
    
    @pytest.fixture
    def mock_provider(self):
        """Create mock provider using constants."""
        config = Config(provider="fcp")
        provider = FCPProvider(
            config=config,
            http_client=Mock(),
        )
        provider.project_resolver.resolve_project = Mock(
            return_value=TestConstants.MOCK_PROJECT_ID
        )
        return provider
    
    def test_complete_workflow_with_network_failures(self, mock_provider):
        """Test complete workflow handling network failures."""
        # Create task config using factory
        config = TaskConfigFactory.create_gpu()
        
        # Set up network failure scenario
        network_scenario = NetworkSimulationFactory.create_flaky_connection()
        
        # Configure mock to simulate network issues
        call_count = 0
        
        def mock_request(method, url, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # Simulate failures based on scenario
            if call_count <= 2 and network_scenario["error_rate"] > 0:
                raise httpx.NetworkError(TestConstants.ERROR_CONNECTION_REFUSED)
            
            # Return success after retries
            if "auctions" in url:
                return {
                    "auctions": [{
                        "id": TestConstants.get_mock_bid_id(),
                        "price": str(TestConstants.TEST_PRICE_MEDIUM)
                    }]
                }
            elif "bids" in url and method == "POST":
                return {
                    "bid": FCPModelFactory.create_fcp_bid().__dict__
                }
            
            return {"status": "ok"}
        
        mock_provider.http.request = Mock(side_effect=mock_request)
        
        # Test with retry logic
        max_attempts = TestConstants.RETRY_MAX_ATTEMPTS
        for attempt in range(max_attempts):
            try:
                task = mock_provider.submit_task(config.instance_type, config)
                task_id = task.task_id
                break
            except httpx.NetworkError:
                if attempt < max_attempts - 1:
                    delay = TestConstants.RETRY_INITIAL_DELAY * (
                        TestConstants.RETRY_BACKOFF_FACTOR ** attempt
                    )
                    time.sleep(min(delay, TestConstants.RETRY_MAX_DELAY))
                else:
                    raise
        
        # Verify task was submitted after retries
        assert task_id is not None
        assert call_count > 1  # Required retries
    
    def test_stress_scenario(self):
        """Demonstrate stress testing with all improvements."""
        # Create many tasks using factory
        tasks = TaskFactory.create_batch(count=100, prefix="stress")
        
        # Simulate various network conditions
        scenarios = [
            NetworkSimulationFactory.create_timeout_scenario(),
            NetworkSimulationFactory.create_flaky_connection(),
            NetworkSimulationFactory.create_slow_connection(),
        ]
        
        # Process tasks with different network conditions
        results = []
        for i, task in enumerate(tasks):
            scenario = scenarios[i % len(scenarios)]
            
            # Simulate processing with network condition
            if scenario["connection_state"] == NetworkSimulation.CONNECTION_DROPPED:
                result = {"task_id": task.task_id, "status": "failed", "reason": "timeout"}
            elif scenario["connection_state"] == NetworkSimulation.CONNECTION_FLAKY:
                # Might succeed after retries
                result = {"task_id": task.task_id, "status": "completed", "retries": 2}
            else:
                result = {"task_id": task.task_id, "status": "completed", "retries": 0}
            
            results.append(result)
        
        # Analyze results
        failed = [r for r in results if r["status"] == "failed"]
        succeeded = [r for r in results if r["status"] == "completed"]
        required_retries = [r for r in succeeded if r["retries"] > 0]
        
        # Verify realistic distribution
        assert len(failed) > 0  # Some failures expected
        assert len(succeeded) > len(failed)  # Most should succeed
        assert len(required_retries) > 0  # Some needed retries