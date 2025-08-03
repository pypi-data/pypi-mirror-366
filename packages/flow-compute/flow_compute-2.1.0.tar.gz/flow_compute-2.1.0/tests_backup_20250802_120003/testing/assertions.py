"""Custom assertion helpers for domain objects.

Provides custom assertions for testing Flow SDK domain objects with
clear, detailed error messages that help developers quickly understand
test failures.

Design principles:
- Clear, informative error messages that show differences
- Consistent API across all assertion helpers
- Support for partial matching and flexible comparisons
- Integration with pytest's assertion rewriting for better output
"""

from typing import Any, Dict, List, Optional, Union

from flow.api.models import (
    Task,
    TaskConfig,
    TaskStatus,
    Volume,
    VolumeSpec,
)
from flow.providers.fcp.config import FCPProviderConfig, FCPScriptSizeConfig


class TaskAssertions:
    """Custom assertions for Task objects."""
    
    @staticmethod
    def assert_task_equal(actual: Task, expected: Task, ignore_fields: Optional[List[str]] = None):
        """Assert two tasks are equal, optionally ignoring specified fields."""
        ignore_fields = ignore_fields or []
        
        # Compare all fields except ignored ones
        for field in ["name", "status", "instance_id", "created_at", "started_at", 
                      "completed_at", "cost_per_hour", "total_cost", "num_instances"]:
            if field in ignore_fields:
                continue
                
            actual_val = getattr(actual, field, None)
            expected_val = getattr(expected, field, None)
            
            if actual_val != expected_val:
                raise AssertionError(
                    f"Task.{field} mismatch:\n"
                    f"  Expected: {expected_val!r}\n"
                    f"  Actual:   {actual_val!r}\n"
                    f"  Task name: {actual.name}"
                )
    
    @staticmethod
    def assert_task_status(task: Task, expected_status: TaskStatus):
        """Assert task has expected status with helpful error message."""
        if task.status != expected_status:
            raise AssertionError(
                f"Task status mismatch for '{task.name}':\n"
                f"  Expected: {expected_status.value}\n"
                f"  Actual:   {task.status.value}\n"
                f"  Task ID:  {task.id if hasattr(task, 'id') else 'N/A'}"
            )
    
    @staticmethod
    def assert_task_running(task: Task):
        """Assert task is in running state with instance assigned."""
        TaskAssertions.assert_task_status(task, TaskStatus.RUNNING)
        
        if not task.instance_id:
            raise AssertionError(
                f"Task '{task.name}' is RUNNING but has no instance_id assigned"
            )
        
        if not task.started_at:
            raise AssertionError(
                f"Task '{task.name}' is RUNNING but has no started_at timestamp"
            )
    
    @staticmethod
    def assert_task_completed(task: Task):
        """Assert task completed successfully with all required fields."""
        TaskAssertions.assert_task_status(task, TaskStatus.COMPLETED)
        
        missing_fields = []
        if not task.started_at:
            missing_fields.append("started_at")
        if not task.completed_at:
            missing_fields.append("completed_at")
        if task.total_cost is None:
            missing_fields.append("total_cost")
            
        if missing_fields:
            raise AssertionError(
                f"Task '{task.name}' is COMPLETED but missing required fields: "
                f"{', '.join(missing_fields)}"
            )
        
        if task.completed_at and task.started_at and task.completed_at < task.started_at:
            raise AssertionError(
                f"Task '{task.name}' has invalid timestamps: "
                f"completed_at ({task.completed_at}) < started_at ({task.started_at})"
            )
    
    @staticmethod
    def assert_task_costs(task: Task, min_cost: float = 0.0, max_cost: Optional[float] = None):
        """Assert task costs are within expected range."""
        if task.total_cost is None:
            raise AssertionError(
                f"Task '{task.name}' has no total_cost set"
            )
        
        if task.total_cost < min_cost:
            raise AssertionError(
                f"Task '{task.name}' cost too low:\n"
                f"  Minimum expected: ${min_cost:.2f}\n"
                f"  Actual:          ${task.total_cost:.2f}"
            )
        
        if max_cost is not None and task.total_cost > max_cost:
            raise AssertionError(
                f"Task '{task.name}' cost too high:\n"
                f"  Maximum expected: ${max_cost:.2f}\n"
                f"  Actual:          ${task.total_cost:.2f}"
            )


class VolumeAssertions:
    """Custom assertions for Volume objects."""
    
    @staticmethod
    def assert_volume_equal(actual: Volume, expected: Volume, ignore_fields: Optional[List[str]] = None):
        """Assert two volumes are equal, optionally ignoring specified fields."""
        ignore_fields = ignore_fields or []
        
        for field in ["name", "size_gb", "attached_to", "created_at", "interface"]:
            if field in ignore_fields:
                continue
                
            actual_val = getattr(actual, field, None)
            expected_val = getattr(expected, field, None)
            
            if actual_val != expected_val:
                raise AssertionError(
                    f"Volume.{field} mismatch:\n"
                    f"  Expected: {expected_val!r}\n"
                    f"  Actual:   {actual_val!r}\n"
                    f"  Volume name: {actual.name}"
                )
    
    @staticmethod
    def assert_volume_attached(volume: Volume, instance_id: str):
        """Assert volume is attached to specific instance."""
        if volume.attached_to != instance_id:
            raise AssertionError(
                f"Volume '{volume.name}' attachment mismatch:\n"
                f"  Expected instance: {instance_id}\n"
                f"  Actual instance:   {volume.attached_to or 'None (unattached)'}"
            )
    
    @staticmethod
    def assert_volume_unattached(volume: Volume):
        """Assert volume is not attached to any instance."""
        if volume.attached_to:
            raise AssertionError(
                f"Volume '{volume.name}' should be unattached but is attached to: "
                f"{volume.attached_to}"
            )
    
    @staticmethod
    def assert_volume_size(volume: Volume, expected_size_gb: int, tolerance_gb: int = 0):
        """Assert volume size is within expected range."""
        size_diff = abs(volume.size_gb - expected_size_gb)
        
        if size_diff > tolerance_gb:
            raise AssertionError(
                f"Volume '{volume.name}' size mismatch:\n"
                f"  Expected: {expected_size_gb} GB (±{tolerance_gb} GB)\n"
                f"  Actual:   {volume.size_gb} GB\n"
                f"  Difference: {size_diff} GB"
            )


class ProviderAssertions:
    """Custom assertions for Provider configuration objects."""
    
    @staticmethod
    def assert_fcp_config_equal(actual: FCPProviderConfig, expected: FCPProviderConfig, 
                                ignore_fields: Optional[List[str]] = None):
        """Assert two FCP provider configs are equal."""
        ignore_fields = ignore_fields or []
        
        # Compare top-level fields
        for field in ["api_url", "project", "region", "enable_caching", 
                      "cache_ttl_seconds", "connection_pool_size", "debug_mode", "dry_run"]:
            if field in ignore_fields:
                continue
                
            actual_val = getattr(actual, field, None)
            expected_val = getattr(expected, field, None)
            
            if actual_val != expected_val:
                raise AssertionError(
                    f"FCPProviderConfig.{field} mismatch:\n"
                    f"  Expected: {expected_val!r}\n"
                    f"  Actual:   {actual_val!r}"
                )
        
        # Compare script size config if not ignored
        if "script_size" not in ignore_fields:
            ProviderAssertions.assert_script_size_config_equal(
                actual.script_size, expected.script_size
            )
    
    @staticmethod
    def assert_script_size_config_equal(actual: FCPScriptSizeConfig, expected: FCPScriptSizeConfig):
        """Assert two script size configs are equal."""
        for field in ["max_script_size", "safety_margin", "enable_compression",
                      "enable_split_storage", "enable_metrics", "enable_health_checks",
                      "compression_level", "max_retries", "request_timeout_seconds"]:
            actual_val = getattr(actual, field, None)
            expected_val = getattr(expected, field, None)
            
            if actual_val != expected_val:
                raise AssertionError(
                    f"FCPScriptSizeConfig.{field} mismatch:\n"
                    f"  Expected: {expected_val!r}\n"
                    f"  Actual:   {actual_val!r}"
                )
    
    @staticmethod
    def assert_fcp_config_valid(config: FCPProviderConfig):
        """Assert FCP provider config passes validation."""
        try:
            config.validate()
        except Exception as e:
            raise AssertionError(
                f"FCPProviderConfig validation failed:\n"
                f"  Error: {str(e)}\n"
                f"  Config: {config}"
            )
    
    @staticmethod
    def assert_fcp_config_invalid(config: FCPProviderConfig, expected_error: Optional[str] = None):
        """Assert FCP provider config fails validation."""
        try:
            config.validate()
            raise AssertionError(
                f"Expected FCPProviderConfig validation to fail, but it passed:\n"
                f"  Config: {config}"
            )
        except ValueError as e:
            if expected_error and expected_error not in str(e):
                raise AssertionError(
                    f"FCPProviderConfig validation failed with unexpected error:\n"
                    f"  Expected error containing: {expected_error}\n"
                    f"  Actual error: {str(e)}"
                )


class TaskConfigAssertions:
    """Custom assertions for TaskConfig objects."""
    
    @staticmethod
    def assert_task_config_has_gpu(config: TaskConfig, expected_gpu_type: Optional[str] = None):
        """Assert task config has GPU configuration."""
        if not config.instance_type:
            raise AssertionError(
                f"TaskConfig '{config.name}' has no instance_type set"
            )
        
        # Simple check for GPU instance types (e.g., "8xH100", "A100", etc.)
        has_gpu = any(gpu in config.instance_type.upper() 
                      for gpu in ["H100", "A100", "V100", "T4", "RTX"])
        
        if not has_gpu:
            raise AssertionError(
                f"TaskConfig '{config.name}' instance_type '{config.instance_type}' "
                f"does not appear to be a GPU instance"
            )
        
        if expected_gpu_type and expected_gpu_type.upper() not in config.instance_type.upper():
            raise AssertionError(
                f"TaskConfig '{config.name}' GPU type mismatch:\n"
                f"  Expected GPU type: {expected_gpu_type}\n"
                f"  Actual instance:   {config.instance_type}"
            )
    
    @staticmethod
    def assert_task_config_has_volumes(config: TaskConfig, expected_count: Optional[int] = None):
        """Assert task config has volumes configured."""
        if not config.volumes:
            raise AssertionError(
                f"TaskConfig '{config.name}' has no volumes configured"
            )
        
        actual_count = len(config.volumes)
        if expected_count is not None and actual_count != expected_count:
            raise AssertionError(
                f"TaskConfig '{config.name}' volume count mismatch:\n"
                f"  Expected: {expected_count} volumes\n"
                f"  Actual:   {actual_count} volumes"
            )
    
    @staticmethod
    def assert_task_config_distributed(config: TaskConfig, min_instances: int = 2):
        """Assert task config is set up for distributed execution."""
        if config.num_instances < min_instances:
            raise AssertionError(
                f"TaskConfig '{config.name}' not configured for distributed execution:\n"
                f"  Minimum instances required: {min_instances}\n"
                f"  Actual num_instances:       {config.num_instances}"
            )


# Convenience functions for common assertions
def assert_task_status(task: Task, expected_status: TaskStatus):
    """Assert task has expected status."""
    TaskAssertions.assert_task_status(task, expected_status)


def assert_task_running(task: Task):
    """Assert task is running with proper state."""
    TaskAssertions.assert_task_running(task)


def assert_task_completed(task: Task):
    """Assert task completed successfully."""
    TaskAssertions.assert_task_completed(task)


def assert_volume_attached(volume: Volume, instance_id: str):
    """Assert volume is attached to instance."""
    VolumeAssertions.assert_volume_attached(volume, instance_id)


def assert_volume_unattached(volume: Volume):
    """Assert volume is not attached."""
    VolumeAssertions.assert_volume_unattached(volume)


def assert_fcp_config_valid(config: FCPProviderConfig):
    """Assert FCP provider config is valid."""
    ProviderAssertions.assert_fcp_config_valid(config)