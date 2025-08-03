"""Test data factories using the Builder pattern.

Provides factory functions and builders for creating test data with sensible
defaults. This complements the builders.py module by providing pre-configured
factories for common test scenarios.

Design principles:
- Factories return fully configured objects for specific test scenarios
- Builders provide fine-grained control when needed
- All factories use TestConstants to avoid magic values
- Immutable factory methods that return new instances
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flow.api.models import (
    AvailableInstance,
    Instance,
    InstanceStatus,
    StorageInterface,
    Task,
    TaskConfig,
    TaskStatus,
    User,
    Volume,
    VolumeSpec,
)
from flow.providers.fcp.config import FCPProviderConfig, FCPScriptSizeConfig
from flow.providers.fcp.core.models import FCPBid, FCPInstance

from .builders import (
    InstanceBuilder,
    TaskBuilder,
    TaskConfigBuilder,
    VolumeBuilder,
)
from .constants import NetworkSimulation, TestConstants


class TaskFactory:
    """Factory for creating Task objects for testing.
    
    Provides pre-configured Task objects for common test scenarios.
    Uses the builder pattern internally for flexibility.
    """
    
    @staticmethod
    def create_pending(
        name: Optional[str] = None,
        instance_type: Optional[str] = None
    ) -> Task:
        """Create a pending task."""
        builder = TaskBuilder()
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_task_name("pending"))
        
        if instance_type:
            builder = builder.with_instance_type(instance_type)
        
        return builder.with_status(TaskStatus.PENDING).build()
    
    @staticmethod
    def create_running(
        name: Optional[str] = None,
        instance_id: Optional[str] = None,
        duration_hours: float = 0.5
    ) -> Task:
        """Create a running task with instance."""
        builder = TaskBuilder()
        
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_task_name("running"))
        
        if instance_id:
            builder = builder.with_instance_id(instance_id)
        else:
            builder = builder.with_instance_id(TestConstants.get_mock_instance_id())
        
        # Set costs
        builder = builder.with_cost_per_hour(TestConstants.TEST_PRICE_MEDIUM)
        
        # Set to running state
        return builder.running().build()
    
    @staticmethod
    def create_completed(
        name: Optional[str] = None,
        duration_hours: float = TestConstants.TEST_DURATION_HOURS,
        total_cost: Optional[float] = None
    ) -> Task:
        """Create a completed task."""
        builder = TaskBuilder()
        
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_task_name("completed"))
        
        builder = builder.with_cost_per_hour(TestConstants.TEST_PRICE_MEDIUM)
        
        if total_cost:
            builder = builder.with_total_cost(total_cost)
        
        return builder.completed(duration_hours).build()
    
    @staticmethod
    def create_failed(
        name: Optional[str] = None,
        error_message: str = "Task failed due to resource allocation error"
    ) -> Task:
        """Create a failed task."""
        builder = TaskBuilder()
        
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_task_name("failed"))
        
        task = builder.with_status(TaskStatus.FAILED).build()
        # Add error details if the Task model supports it
        return task
    
    @staticmethod
    def create_with_volumes(
        name: Optional[str] = None,
        volume_count: int = 2
    ) -> Task:
        """Create a task with attached volumes."""
        builder = TaskBuilder()
        
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_task_name("volumes"))
        
        # Note: Task model doesn't directly store volumes, this is for reference
        return builder.running().build()
    
    @staticmethod
    def create_multi_instance(
        name: Optional[str] = None,
        num_instances: int = 4
    ) -> Task:
        """Create a multi-instance task."""
        task_name = name or TestConstants.get_test_task_name("multi")
        
        task = TaskBuilder().with_name(task_name).running().build()
        
        # Generate instance IDs
        task.instances = [
            f"{TestConstants.TEST_INSTANCE_PREFIX}{i:03d}"
            for i in range(num_instances)
        ]
        task.num_instances = num_instances
        
        return task
    
    @staticmethod
    def create_gpu_task(
        gpu_type: str = TestConstants.DEFAULT_GPU_TYPE,
        num_gpus: int = 1
    ) -> Task:
        """Create a GPU task."""
        name = TestConstants.get_test_task_name(f"gpu-{gpu_type}")
        
        return (TaskBuilder()
                .with_name(name)
                .with_instance_type(gpu_type)
                .with_cost_per_hour(TestConstants.TEST_PRICE_HIGH)
                .running()
                .build())
    
    @staticmethod
    def create_batch(
        count: int = 5,
        prefix: str = "batch"
    ) -> List[Task]:
        """Create a batch of tasks with mixed statuses."""
        tasks = []
        
        # Create tasks with different statuses
        status_distribution = [
            (TaskStatus.PENDING, count // 5),
            (TaskStatus.RUNNING, count // 5 * 2),
            (TaskStatus.COMPLETED, count // 5 * 2),
        ]
        
        task_index = 0
        for status, status_count in status_distribution:
            for i in range(status_count):
                name = f"{prefix}-{task_index:03d}"
                
                if status == TaskStatus.PENDING:
                    task = TaskFactory.create_pending(name)
                elif status == TaskStatus.RUNNING:
                    task = TaskFactory.create_running(name)
                else:
                    task = TaskFactory.create_completed(name)
                
                tasks.append(task)
                task_index += 1
        
        # Fill remainder with completed tasks
        while len(tasks) < count:
            name = f"{prefix}-{task_index:03d}"
            tasks.append(TaskFactory.create_completed(name))
            task_index += 1
        
        return tasks


class TaskConfigFactory:
    """Factory for creating TaskConfig objects for testing."""
    
    @staticmethod
    def create_simple(
        name: Optional[str] = None,
        command: Optional[str] = None
    ) -> TaskConfig:
        """Create a simple task configuration."""
        builder = TaskConfigBuilder()
        
        if name:
            builder = builder.with_name(name)
        
        if command:
            builder = builder.with_command(command)
        
        return builder.build()
    
    @staticmethod
    def create_gpu(
        gpu_type: str = TestConstants.DEFAULT_GPU_TYPE,
        region: Optional[str] = None
    ) -> TaskConfig:
        """Create a GPU task configuration."""
        builder = (TaskConfigBuilder()
                   .with_gpu(gpu_type)
                   .with_max_price(TestConstants.TEST_PRICE_HIGH))
        
        if region:
            builder = builder.with_region(region)
        
        return builder.build()
    
    @staticmethod
    def create_with_volumes(
        volumes: Optional[List[VolumeSpec]] = None
    ) -> TaskConfig:
        """Create a task configuration with volumes."""
        builder = TaskConfigBuilder()
        
        if volumes:
            builder = builder.with_volumes(volumes)
        else:
            # Default volumes
            builder = (builder
                       .with_volume("/data", 100)
                       .with_volume("/models", 50))
        
        return builder.build()
    
    @staticmethod
    def create_with_environment(
        env_vars: Optional[Dict[str, str]] = None
    ) -> TaskConfig:
        """Create a task configuration with environment variables."""
        builder = TaskConfigBuilder()
        
        if env_vars:
            builder = builder.with_environment(env_vars)
        else:
            # Default test environment
            builder = builder.with_environment(TestConstants.TEST_ENV_VARS)
        
        return builder.build()
    
    @staticmethod
    def create_distributed(
        num_instances: int = 4,
        upload_code: bool = True
    ) -> TaskConfig:
        """Create a distributed task configuration."""
        return (TaskConfigBuilder()
                .with_num_instances(num_instances)
                .with_upload_code(upload_code)
                .with_script("python train_distributed.py")
                .build())
    
    @staticmethod
    def create_invalid() -> TaskConfig:
        """Create an invalid task configuration for error testing."""
        # Create config with invalid values that should fail validation
        config = TaskConfigBuilder().build()
        # Force invalid state (normally prevented by Pydantic)
        config.name = ""  # Empty name
        config.instance_type = ""  # Empty instance type
        return config


class VolumeFactory:
    """Factory for creating Volume objects for testing."""
    
    @staticmethod
    def create_unattached(
        name: Optional[str] = None,
        size_gb: int = TestConstants.DEFAULT_VOLUME_SIZE_GB
    ) -> Volume:
        """Create an unattached volume."""
        builder = VolumeBuilder()
        
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_volume_name())
        
        return builder.with_size(size_gb).build()
    
    @staticmethod
    def create_attached(
        instance_id: str,
        name: Optional[str] = None
    ) -> Volume:
        """Create a volume attached to an instance."""
        builder = VolumeBuilder()
        
        if name:
            builder = builder.with_name(name)
        else:
            builder = builder.with_name(TestConstants.get_test_volume_name("attached"))
        
        return builder.attached_to(instance_id).build()
    
    @staticmethod
    def create_large(size_gb: int = 1000) -> Volume:
        """Create a large volume for capacity testing."""
        return (VolumeBuilder()
                .with_name(TestConstants.get_test_volume_name("large"))
                .with_size(size_gb)
                .build())
    
    @staticmethod
    def create_file_share() -> Volume:
        """Create a file share volume."""
        return (VolumeBuilder()
                .with_name(TestConstants.get_test_volume_name("share"))
                .with_interface(StorageInterface.FILE)
                .with_size(100)
                .build())


class InstanceFactory:
    """Factory for creating Instance objects for testing."""
    
    @staticmethod
    def create_available(
        instance_type: str = TestConstants.DEFAULT_INSTANCE_TYPE,
        region: str = TestConstants.DEFAULT_REGION,
        price: float = TestConstants.TEST_PRICE_MEDIUM
    ) -> AvailableInstance:
        """Create an available instance."""
        return (InstanceBuilder()
                .with_type(instance_type)
                .with_region(region)
                .with_price(price)
                .build())
    
    @staticmethod
    def create_gpu_instance(
        gpu_type: str = "H100",
        gpu_count: int = 8
    ) -> AvailableInstance:
        """Create a GPU instance."""
        return (InstanceBuilder()
                .with_type(f"{gpu_count}x{gpu_type}")
                .with_gpu_info(gpu_type, gpu_count)
                .with_price(TestConstants.TEST_PRICE_HIGH)
                .build())


class FCPModelFactory:
    """Factory for creating FCP-specific model objects for testing."""
    
    @staticmethod
    def create_fcp_bid(
        status: str = "pending",
        name: Optional[str] = None
    ) -> FCPBid:
        """Create an FCP bid for testing."""
        return FCPBid(
            fid=TestConstants.get_mock_bid_id(),
            name=name or TestConstants.get_test_task_name(),
            status=status,
            limit_price=str(TestConstants.TEST_PRICE_MEDIUM),
            created_at=datetime.now(),
            project=TestConstants.MOCK_PROJECT_ID,
            created_by=TestConstants.MOCK_USER_ID,
            instance_quantity=TestConstants.DEFAULT_NUM_INSTANCES,
            instance_type=TestConstants.TEST_INSTANCE_TYPE_ID,
            region=TestConstants.DEFAULT_REGION,
        )
    
    @staticmethod
    def create_fcp_instance(
        bid_id: str,
        status: str = "running"
    ) -> FCPInstance:
        """Create an FCP instance for testing."""
        return FCPInstance(
            fid=TestConstants.get_mock_instance_id(),
            bid_id=bid_id,
            status=status,
            created_at=datetime.now(),
            instance_type=TestConstants.TEST_INSTANCE_TYPE_ID,
            region=TestConstants.DEFAULT_REGION,
        )


class ProviderConfigFactory:
    """Factory for creating Provider configuration objects for testing.
    
    Provides pre-configured provider configurations for common test scenarios.
    Currently supports FCP provider configurations.
    """
    
    @staticmethod
    def create_fcp_default() -> FCPProviderConfig:
        """Create default FCP provider configuration."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            region=TestConstants.DEFAULT_REGION,
            script_size=FCPScriptSizeConfig(
                max_script_size=10_000,
                safety_margin=1_000,
                enable_compression=True,
                enable_split_storage=True,
            ),
        )
    
    @staticmethod
    def create_fcp_minimal() -> FCPProviderConfig:
        """Create minimal FCP configuration for simple tests."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            script_size=FCPScriptSizeConfig(
                max_script_size=5_000,
                enable_compression=False,
                enable_split_storage=False,
                enable_metrics=False,
                enable_health_checks=False,
            ),
            enable_caching=False,
            debug_mode=False,
        )
    
    @staticmethod
    def create_fcp_with_compression() -> FCPProviderConfig:
        """Create FCP configuration with compression enabled."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            script_size=FCPScriptSizeConfig(
                max_script_size=10_000,
                safety_margin=2_000,
                enable_compression=True,
                compression_level=9,
                enable_split_storage=False,
            ),
        )
    
    @staticmethod
    def create_fcp_with_split_storage() -> FCPProviderConfig:
        """Create FCP configuration with split storage enabled."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            script_size=FCPScriptSizeConfig(
                max_script_size=5_000,  # Lower limit to trigger splits
                safety_margin=500,
                enable_compression=False,
                enable_split_storage=True,
                storage_backend="local",
            ),
        )
    
    @staticmethod
    def create_fcp_debug() -> FCPProviderConfig:
        """Create FCP configuration for debugging."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            region=TestConstants.DEFAULT_REGION,
            script_size=FCPScriptSizeConfig(
                enable_detailed_logging=True,
                enable_metrics=True,
            ),
            debug_mode=True,
            dry_run=False,
        )
    
    @staticmethod
    def create_fcp_dry_run() -> FCPProviderConfig:
        """Create FCP configuration for dry-run testing."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            debug_mode=True,
            dry_run=True,
        )
    
    @staticmethod
    def create_fcp_multi_region(regions: List[str] = None) -> FCPProviderConfig:
        """Create FCP configuration for multi-region testing."""
        if regions is None:
            regions = [TestConstants.DEFAULT_REGION, "europe-west4", "asia-south1"]
        
        # Return config for first region, typically used with multiple instances
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            region=regions[0],
        )
    
    @staticmethod
    def create_fcp_with_custom_limits(
        max_script_size: int = 15_000,
        cache_ttl: int = 600,
        pool_size: int = 100
    ) -> FCPProviderConfig:
        """Create FCP configuration with custom resource limits."""
        return FCPProviderConfig(
            api_url="https://api.mlfoundry.com",
            project=TestConstants.MOCK_PROJECT_ID,
            script_size=FCPScriptSizeConfig(
                max_script_size=max_script_size,
                safety_margin=max_script_size // 10,
                max_retries=5,
                request_timeout_seconds=60,
            ),
            cache_ttl_seconds=cache_ttl,
            connection_pool_size=pool_size,
        )
    
    @staticmethod
    def create_fcp_invalid() -> FCPProviderConfig:
        """Create invalid FCP configuration for error testing."""
        # Create config that will fail validation
        config = FCPProviderConfig(
            api_url="",  # Invalid empty URL
            project="",  # Invalid empty project
            script_size=FCPScriptSizeConfig(
                max_script_size=-1,  # Invalid negative size
                compression_level=0,  # Invalid compression level
            ),
            cache_ttl_seconds=-1,  # Invalid negative TTL
            connection_pool_size=0,  # Invalid pool size
        )
        return config


class NetworkSimulationFactory:
    """Factory for creating network simulation scenarios."""
    
    @staticmethod
    def create_timeout_scenario() -> Dict[str, any]:
        """Create a network timeout scenario."""
        return {
            "latency": NetworkSimulation.LATENCY_TIMEOUT,
            "packet_loss": NetworkSimulation.PACKET_LOSS_SEVERE,
            "bandwidth": NetworkSimulation.BANDWIDTH_SLOW,
            "connection_state": NetworkSimulation.CONNECTION_DROPPED,
        }
    
    @staticmethod
    def create_flaky_connection() -> Dict[str, any]:
        """Create a flaky connection scenario."""
        return {
            "latency": NetworkSimulation.LATENCY_HIGH,
            "packet_loss": NetworkSimulation.PACKET_LOSS_MEDIUM,
            "bandwidth": NetworkSimulation.BANDWIDTH_MEDIUM,
            "connection_state": NetworkSimulation.CONNECTION_FLAKY,
            "error_rate": NetworkSimulation.ERROR_RATE_MEDIUM,
        }
    
    @staticmethod
    def create_slow_connection() -> Dict[str, any]:
        """Create a slow but stable connection."""
        return {
            "latency": NetworkSimulation.LATENCY_VERY_HIGH,
            "packet_loss": NetworkSimulation.PACKET_LOSS_LOW,
            "bandwidth": NetworkSimulation.BANDWIDTH_SLOW,
            "connection_state": NetworkSimulation.CONNECTION_SLOW,
        }