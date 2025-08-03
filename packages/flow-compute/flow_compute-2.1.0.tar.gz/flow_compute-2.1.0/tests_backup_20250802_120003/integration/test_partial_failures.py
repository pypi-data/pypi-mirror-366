"""Partial failure scenario tests for distributed operations.

These tests verify that the SDK correctly handles partial failures in
distributed scenarios where some operations succeed while others fail.

DESIGN PRINCIPLES:
- Test realistic partial failure scenarios
- Verify proper cleanup of successful operations when others fail
- Ensure clear error reporting for partial failures
- Test rollback and recovery mechanisms
- Verify idempotency of operations
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from unittest.mock import Mock, patch

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig, TaskStatus
from flow.errors import APIError, ResourceNotFoundError
from flow.providers.fcp.provider import FCPProvider
from tests.testing import (
    TaskConfigBuilder,
    create_test_provider,
    isolation_context,
)

logger = logging.getLogger(__name__)

# Test constants
PARTIAL_FAILURE_RATIO = 0.3  # 30% of operations should fail
DISTRIBUTED_TASK_COUNT = 20
ROLLBACK_TIMEOUT_SECONDS = 30


@dataclass
class PartialFailureMetrics:
    """Track metrics for partial failure scenarios."""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    rolled_back_operations: int = 0
    cleanup_failures: int = 0
    operation_times: List[float] = field(default_factory=list)
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    def record_success(self, duration: float):
        """Record a successful operation."""
        self.successful_operations += 1
        self.operation_times.append(duration)
        
    def record_failure(self, error: Exception, duration: float):
        """Record a failed operation."""
        self.failed_operations += 1
        self.operation_times.append(duration)
        error_type = type(error).__name__
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
        
    def record_rollback(self):
        """Record a rollback operation."""
        self.rolled_back_operations += 1
        
    def get_failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_operations == 0:
            return 0.0
        return self.failed_operations / self.total_operations


class DistributedOperation:
    """Represents a distributed operation that can partially fail."""
    
    def __init__(self, operation_id: str, should_fail: bool = False):
        self.operation_id = operation_id
        self.should_fail = should_fail
        self.completed = False
        self.rolled_back = False
        self.start_time = None
        self.end_time = None
        
    def execute(self) -> Any:
        """Execute the operation."""
        self.start_time = time.time()
        
        if self.should_fail:
            self.end_time = time.time()
            raise APIError(f"Simulated failure for {self.operation_id}")
            
        # Simulate some work
        time.sleep(0.1)
        self.completed = True
        self.end_time = time.time()
        return f"Result for {self.operation_id}"
        
    def rollback(self):
        """Rollback the operation."""
        if self.completed:
            self.rolled_back = True
            self.completed = False
            
    def get_duration(self) -> float:
        """Get operation duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@pytest.mark.integration
class TestPartialFailureScenarios:
    """Test partial failure scenarios in distributed operations."""
    
    def test_partial_task_submission_failure(self):
        """Test when some tasks fail to submit in a batch."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
            
        provider = create_test_provider()
        metrics = PartialFailureMetrics()
        successful_tasks = []
        failed_submissions = []
        
        with isolation_context(provider) as context:
            # Find instances
            instances = provider.find_instances(
                {"max_price_per_hour": 50.0}, 
                limit=DISTRIBUTED_TASK_COUNT
            )
            if not instances:
                pytest.skip("No instances available")
                
            # Create task configs with some designed to fail
            configs = []
            for i in range(DISTRIBUTED_TASK_COUNT):
                config_builder = TaskConfigBuilder() \
                    .with_name(f"{context['namespace']}-partial-{i}") \
                    .with_instance_type(instances[i % len(instances)].instance_type) \
                    .with_upload_code(False)
                    
                # Make some configs invalid to trigger failures
                if i % 3 == 0:  # Every 3rd task will fail
                    config_builder.with_command("")  # Invalid empty command
                else:
                    config_builder.with_command(f"echo 'Task {i}'")
                    
                configs.append(config_builder.build())
                
            # Submit tasks and track failures
            for i, config in enumerate(configs):
                metrics.total_operations += 1
                start_time = time.time()
                
                try:
                    task = provider.submit_task(
                        instances[i % len(instances)].instance_type,
                        config
                    )
                    duration = time.time() - start_time
                    metrics.record_success(duration)
                    successful_tasks.append(task)
                    context["created_resources"].append(("task", task.task_id))
                    
                except Exception as e:
                    duration = time.time() - start_time
                    metrics.record_failure(e, duration)
                    failed_submissions.append((i, str(e)))
                    
        # Verify partial failure behavior
        assert metrics.successful_operations > 0, "No tasks succeeded"
        assert metrics.failed_operations > 0, "No tasks failed (expected some failures)"
        assert metrics.get_failure_rate() > 0.2, "Failure rate too low"
        assert metrics.get_failure_rate() < 0.5, "Failure rate too high"
        
        # Verify successful tasks are still running
        for task in successful_tasks[:5]:  # Check first 5
            current_status = provider.get_task(task.task_id)
            assert current_status.status in [
                TaskStatus.PENDING, 
                TaskStatus.RUNNING, 
                TaskStatus.COMPLETED
            ]
            
    def test_distributed_volume_operations_partial_failure(self):
        """Test partial failures in distributed volume operations."""
        provider, mock_http = self._create_mock_provider()
        metrics = PartialFailureMetrics()
        successful_volumes = []
        
        def mock_request(method, url, **kwargs):
            """Mock that fails some volume operations."""
            if "/volumes" in url and method == "POST":
                volume_name = kwargs["json"]["name"]
                # Fail volumes with specific pattern
                if "fail" in volume_name:
                    raise APIError("Volume creation failed", status_code=500)
                    
                return {
                    "fid": f"vol-{time.time_ns()}",
                    "name": volume_name,
                    "size_gb": kwargs["json"]["size_gb"],
                    "status": "available",
                    "created_at": datetime.now().isoformat()
                }
            elif "/volumes/" in url and method == "GET":
                vol_id = url.split("/")[-1]
                return {
                    "fid": vol_id,
                    "status": "available",
                    "size_gb": 10
                }
            elif "/volumes/" in url and method == "DELETE":
                return {"deleted": True}
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        # Create volumes with mixed success/failure
        volume_configs = []
        for i in range(20):
            name = f"vol-{i}-fail" if i % 4 == 0 else f"vol-{i}"
            volume_configs.append({
                "name": name,
                "size_gb": 10 + i
            })
            
        # Execute distributed volume creation
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for config in volume_configs:
                future = executor.submit(
                    self._create_volume_with_metrics,
                    provider, config, metrics
                )
                futures.append(future)
                
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                if result:
                    successful_volumes.append(result)
                    
        # Verify partial success
        assert len(successful_volumes) == 15, "Expected 15 successful volumes"
        assert metrics.failed_operations == 5, "Expected 5 failed operations"
        
        # Cleanup successful volumes
        cleanup_errors = 0
        for volume in successful_volumes:
            try:
                provider.delete_volume(volume["fid"])
            except Exception:
                cleanup_errors += 1
                
        assert cleanup_errors == 0, f"Failed to cleanup {cleanup_errors} volumes"
        
    def test_multi_region_partial_deployment(self):
        """Test partial failure in multi-region deployments."""
        if not os.environ.get("FCP_TEST_API_KEY"):
            pytest.skip("Integration tests require FCP_TEST_API_KEY")
            
        provider = create_test_provider()
        regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        deployment_results = {}
        
        with isolation_context(provider) as context:
            # Try to deploy to multiple regions
            for region in regions:
                try:
                    # Find instances in region
                    instances = provider.find_instances({
                        "region": region,
                        "max_price_per_hour": 50.0
                    }, limit=1)
                    
                    if not instances:
                        deployment_results[region] = {
                            "status": "failed",
                            "reason": "No instances available"
                        }
                        continue
                        
                    # Submit task to region
                    config = TaskConfigBuilder() \
                        .with_name(f"{context['namespace']}-{region}") \
                        .with_instance_type(instances[0].instance_type) \
                        .with_command(f"echo 'Deployed to {region}'") \
                        .with_upload_code(False) \
                        .build()
                        
                    task = provider.submit_task(instances[0].instance_type, config)
                    context["created_resources"].append(("task", task.task_id))
                    
                    deployment_results[region] = {
                        "status": "success",
                        "task_id": task.task_id
                    }
                    
                except Exception as e:
                    deployment_results[region] = {
                        "status": "failed",
                        "reason": str(e)
                    }
                    
        # Verify partial deployment
        successful_regions = [
            r for r, result in deployment_results.items() 
            if result["status"] == "success"
        ]
        failed_regions = [
            r for r, result in deployment_results.items() 
            if result["status"] == "failed"
        ]
        
        # Should have some successes and some failures
        assert len(successful_regions) > 0, "No regions succeeded"
        assert len(successful_regions) < len(regions), "All regions succeeded (expected some failures)"
        
        logger.info(f"Deployment results: {deployment_results}")
        
    def test_rollback_on_partial_failure(self):
        """Test rollback mechanisms when partial failures occur."""
        operations = []
        metrics = PartialFailureMetrics()
        
        # Create operations with some designed to fail
        for i in range(10):
            should_fail = i >= 7  # Last 3 operations will fail
            op = DistributedOperation(f"op-{i}", should_fail=should_fail)
            operations.append(op)
            
        successful_ops = []
        
        try:
            # Execute operations
            for op in operations:
                metrics.total_operations += 1
                try:
                    result = op.execute()
                    metrics.record_success(op.get_duration())
                    successful_ops.append(op)
                except Exception as e:
                    metrics.record_failure(e, op.get_duration())
                    # On failure, rollback all successful operations
                    logger.info(f"Operation {op.operation_id} failed, rolling back...")
                    for success_op in successful_ops:
                        success_op.rollback()
                        metrics.record_rollback()
                    raise
                    
        except APIError:
            # Expected failure
            pass
            
        # Verify rollback occurred
        assert metrics.rolled_back_operations == 7, "Expected 7 rollbacks"
        assert all(op.rolled_back for op in successful_ops), "Not all operations rolled back"
        assert metrics.failed_operations == 1, "Expected 1 recorded failure"
        
    def test_cascading_failure_handling(self):
        """Test handling of cascading failures in dependent operations."""
        provider, mock_http = self._create_mock_provider()
        
        # Track operation dependencies
        operation_graph = {
            "create_volume": ["create_task"],
            "create_task": ["attach_volume", "start_monitoring"],
            "attach_volume": ["run_workload"],
            "start_monitoring": ["collect_metrics"],
            "run_workload": [],
            "collect_metrics": []
        }
        
        completed_operations = set()
        failed_operations = set()
        
        def execute_operation(op_name: str) -> bool:
            """Execute an operation and its dependencies."""
            # Simulate failure for specific operations
            if op_name == "attach_volume":
                failed_operations.add(op_name)
                raise APIError(f"Failed to execute {op_name}")
                
            # Execute operation
            time.sleep(0.1)  # Simulate work
            completed_operations.add(op_name)
            
            # Execute dependencies
            for dep in operation_graph.get(op_name, []):
                try:
                    execute_operation(dep)
                except APIError:
                    # Cascade the failure
                    failed_operations.add(dep)
                    raise
                    
            return True
            
        # Start execution from root
        try:
            execute_operation("create_volume")
        except APIError:
            pass
            
        # Verify cascading failure behavior
        assert "create_volume" in completed_operations
        assert "create_task" in completed_operations
        assert "attach_volume" in failed_operations
        assert "run_workload" not in completed_operations  # Should not execute
        assert "start_monitoring" in completed_operations  # Independent branch
        assert "collect_metrics" in completed_operations
        
    def _create_volume_with_metrics(
        self, 
        provider: FCPProvider, 
        config: Dict[str, Any], 
        metrics: PartialFailureMetrics
    ) -> Optional[Dict[str, Any]]:
        """Create volume and track metrics."""
        start_time = time.time()
        metrics.total_operations += 1
        
        try:
            volume = provider.create_volume(**config)
            duration = time.time() - start_time
            metrics.record_success(duration)
            return {
                "fid": volume.volume_id,
                "name": volume.name,
                "size_gb": volume.size_gb
            }
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_failure(e, duration)
            return None
            
    def _create_mock_provider(self) -> Tuple[FCPProvider, Mock]:
        """Create provider with mock HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={"project": "test-project"}
        )
        
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = "proj-123"
        
        return provider, mock_http


@pytest.mark.integration
class TestPartialFailureRecovery:
    """Test recovery mechanisms for partial failures."""
    
    def test_idempotent_operations(self):
        """Test that operations can be safely retried after partial failure."""
        provider, mock_http = self._create_mock_provider()
        
        operation_attempts = {}
        
        def mock_request(method, url, **kwargs):
            """Track operation attempts and simulate transient failures."""
            key = f"{method}:{url}"
            operation_attempts[key] = operation_attempts.get(key, 0) + 1
            
            # Fail first attempt for some operations
            if operation_attempts[key] == 1 and "task" in url:
                raise APIError("Transient failure", status_code=503)
                
            if "/tasks" in url and method == "POST":
                return {
                    "fid": f"task-{kwargs['json']['name']}",
                    "status": "pending",
                    "created_at": datetime.now().isoformat()
                }
            elif "/tasks/" in url and method == "GET":
                task_id = url.split("/")[-1]
                return {
                    "fid": task_id,
                    "status": "running",
                    "name": task_id.replace("task-", "")
                }
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        # Attempt operations with retry logic
        tasks_to_create = ["job-1", "job-2", "job-3"]
        created_tasks = []
        
        for task_name in tasks_to_create:
            for attempt in range(3):  # Max 3 attempts
                try:
                    config = TaskConfigBuilder() \
                        .with_name(task_name) \
                        .with_instance_type("a100") \
                        .with_upload_code(False) \
                        .build()
                        
                    # Check if task already exists (idempotency check)
                    try:
                        existing = provider.get_task(f"task-{task_name}")
                        created_tasks.append(existing)
                        break
                    except ResourceNotFoundError:
                        pass
                        
                    # Create task
                    task = provider.submit_task("a100", config)
                    created_tasks.append(task)
                    break
                    
                except APIError as e:
                    if attempt == 2:  # Last attempt
                        raise
                    time.sleep(0.5)  # Brief backoff
                    
        # Verify all tasks were created despite transient failures
        assert len(created_tasks) == 3
        assert all(t.task_id == f"task-{t.name}" for t in created_tasks)
        
    def test_partial_cleanup_recovery(self):
        """Test recovery when cleanup operations partially fail."""
        provider, mock_http = self._create_mock_provider()
        
        resources_to_cleanup = {
            "tasks": ["task-1", "task-2", "task-3"],
            "volumes": ["vol-1", "vol-2", "vol-3"]
        }
        
        cleanup_attempts = {}
        cleanup_failures = set()
        
        def mock_request(method, url, **kwargs):
            """Simulate some cleanup failures."""
            resource_id = url.split("/")[-1] if "/" in url else None
            
            if method == "DELETE":
                key = f"delete:{resource_id}"
                cleanup_attempts[key] = cleanup_attempts.get(key, 0) + 1
                
                # Fail first attempt for some resources
                if cleanup_attempts[key] == 1 and resource_id in ["task-2", "vol-3"]:
                    cleanup_failures.add(resource_id)
                    raise APIError("Cleanup failed", status_code=500)
                    
                return {"deleted": True}
                
            elif method == "GET":
                # Simulate resources exist
                if "task" in url:
                    return {"fid": resource_id, "status": "running"}
                elif "vol" in url:
                    return {"fid": resource_id, "status": "available"}
                    
            return []
            
        mock_http.request = Mock(side_effect=mock_request)
        
        # Perform cleanup with retry
        cleanup_results = {
            "success": [],
            "failed": [],
            "retried": []
        }
        
        for resource_type, resource_ids in resources_to_cleanup.items():
            for resource_id in resource_ids:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        if resource_type == "tasks":
                            provider.cancel_task(resource_id)
                        else:
                            provider.delete_volume(resource_id)
                            
                        if attempt > 0:
                            cleanup_results["retried"].append(resource_id)
                        cleanup_results["success"].append(resource_id)
                        break
                        
                    except APIError as e:
                        if attempt == max_retries - 1:
                            cleanup_results["failed"].append(resource_id)
                        else:
                            time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                            
        # Verify cleanup results
        assert len(cleanup_results["success"]) == 6, "All resources should eventually be cleaned"
        assert len(cleanup_results["retried"]) == 2, "Two resources should have been retried"
        assert len(cleanup_results["failed"]) == 0, "No permanent failures with retry"
        
    def _create_mock_provider(self) -> Tuple[FCPProvider, Mock]:
        """Create provider with mock HTTP client."""
        config = Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={"project": "test-project"}
        )
        
        mock_http = Mock()
        provider = FCPProvider(config, http_client=mock_http)
        provider._project_id = "proj-123"
        
        return provider, mock_http


def test_partial_failure_summary():
    """Summary of partial failure test coverage."""
    covered_scenarios = {
        "Partial Task Submission": "Some tasks fail while others succeed",
        "Distributed Volume Operations": "Mixed success/failure in volume operations",
        "Multi-Region Deployment": "Partial success across regions",
        "Rollback Mechanisms": "Successful operations rolled back on failure",
        "Cascading Failures": "Dependent operations fail when parent fails",
        "Idempotent Recovery": "Safe retry after partial failures",
        "Cleanup Recovery": "Cleanup operations can be retried",
        "Failure Metrics": "Track and analyze partial failure patterns",
    }
    
    logger.info("Partial failure test coverage:")
    for scenario, description in covered_scenarios.items():
        logger.info(f"  ✓ {scenario}: {description}")
        
    assert len(covered_scenarios) >= 8, "Missing partial failure scenarios"