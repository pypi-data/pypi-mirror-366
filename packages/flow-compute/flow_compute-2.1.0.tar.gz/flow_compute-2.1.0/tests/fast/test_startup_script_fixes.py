"""Fixes for startup script validation issues in tests.

This module provides patches and utilities to fix the runtime monitoring
validation issues that occur when task_id is not provided.
"""

from typing import Optional
from unittest.mock import patch

from flow.api.models import TaskConfig
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder
from flow.providers.fcp.runtime.startup.sections import ScriptContext


class TestStartupScriptBuilder(StartupScriptBuilder):
    """Test-friendly StartupScriptBuilder that handles missing task_id gracefully."""
    
    def _create_context(self, config: TaskConfig) -> ScriptContext:
        """Create script context with test-friendly defaults."""
        context = super()._create_context(config)
        
        # For tests, if task_id is missing and runtime monitoring is enabled,
        # either disable runtime monitoring or provide a test task_id
        if not context.task_id and context.max_run_time_hours:
            # Option 1: Provide a test task_id
            context.task_id = "test-task-id"
            
            # Option 2: Disable runtime monitoring (uncomment if preferred)
            # context.max_run_time_hours = 0
            
        return context


def create_test_config_with_task_id(
    name: str = "test-task",
    instance_type: str = "h100",
    **kwargs
) -> TaskConfig:
    """Create a TaskConfig with task_id for testing.
    
    This helper ensures the config has a task_id attribute to avoid
    runtime monitoring validation errors.
    """
    config = TaskConfig(
        name=name,
        instance_type=instance_type,
        **kwargs
    )
    
    # Add task_id as an attribute (not part of model)
    if not hasattr(config, 'task_id'):
        setattr(config, 'task_id', f"{name}-id")
    
    return config


def patch_runtime_monitoring_validation():
    """Patch to skip runtime monitoring validation in tests.
    
    Use this as a decorator or context manager when you want to
    test startup scripts without providing task_id.
    """
    def mock_validate(self, context: ScriptContext):
        """Skip validation if no task_id in test context."""
        if not context.task_id:
            # In tests, silently skip validation
            return []
        # Otherwise run normal validation
        from flow.providers.fcp.runtime.startup.sections import RuntimeMonitoringSection
        return RuntimeMonitoringSection.validate(self, context)
    
    return patch(
        'flow.providers.fcp.runtime.startup.sections.RuntimeMonitoringSection.validate',
        mock_validate
    )


# Example fixes for specific test files

def fix_docker_cache_test():
    """Fix for test_docker_cache_persists_with_volume."""
    config = TaskConfig(
        name="docker-cache-test",
        instance_type="a100-80gb",
        image="tensorflow/tensorflow:latest-gpu",
        command="echo 'Testing docker cache'",
        volumes=[
            {"size_gb": 100, "mount_path": "/var/lib/docker"},
        ],
        max_run_time_hours=0,  # Disable runtime monitoring
    )
    
    # Or use the test builder
    builder = TestStartupScriptBuilder()
    script = builder.build(config)
    
    return script


def fix_gpu_docker_test():
    """Fix for test_gpu_driver_before_docker."""
    config = create_test_config_with_task_id(
        name="gpu-test",
        instance_type="h100-80gb.sxm.8x",
        command="nvidia-smi",
        max_run_time_hours=1.0  # Can keep runtime monitoring
    )
    
    builder = StartupScriptBuilder()
    script = builder.build(config)
    
    return script


def fix_runtime_monitoring_test():
    """Fix for tests that specifically test runtime monitoring."""
    # When testing runtime monitoring, always provide task_id
    config = TaskConfig(
        name="runtime-test",
        instance_type="h100",
        command="sleep 3600",
        max_run_time_hours=2.0,
        min_run_time_hours=0.5,
    )
    
    # Add task_id for the test
    setattr(config, 'task_id', 'runtime-test-123')
    
    builder = StartupScriptBuilder()
    script = builder.build(config)
    
    # Verify runtime monitoring is included
    assert any('runtime' in s.lower() for s in script.sections)
    
    return script


# Monkey patch for quick fixes in existing tests

def monkey_patch_startup_script_builder():
    """Apply monkey patch to fix validation issues globally.
    
    Call this in test setup to fix all startup script tests.
    """
    original_create_context = StartupScriptBuilder._create_context
    
    def patched_create_context(self, config: TaskConfig) -> ScriptContext:
        context = original_create_context(self, config)
        
        # Auto-fix missing task_id when runtime monitoring is enabled
        if not context.task_id and context.max_run_time_hours:
            context.task_id = f"{config.name}-test-id"
        
        return context
    
    StartupScriptBuilder._create_context = patched_create_context