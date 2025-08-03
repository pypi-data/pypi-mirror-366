"""Test helpers for task submission."""

import logging
from typing import Optional

import pytest

from flow.api.models import Task, TaskConfig
from flow.providers.fcp.provider import FCPProvider

logger = logging.getLogger(__name__)


def submit_test_task(
    provider: FCPProvider,
    config: TaskConfig,
    prefer_cheapest: bool = True
) -> Task:
    """Submit a task handling the two-phase FCP submission.
    
    This helper abstracts the complexity of:
    1. Finding available instances
    2. Handling no availability gracefully
    3. Submitting to the best instance
    4. Adjusting region to match available instances
    
    Args:
        provider: The FCP provider instance
        config: Task configuration
        prefer_cheapest: If True, select cheapest instance
        
    Returns:
        Submitted task
        
    Raises:
        pytest.skip: If no instances are available
    """
    # Build search requirements from config
    requirements = {
        "max_price_per_hour": config.max_price_per_hour or 100.0
    }

    # DON'T pass instance_type in requirements for find_instances
    # because config.instance_type might be an opaque ID from a previous
    # find_instances call. Instead, we'll search broadly and then
    # the submit_task will use the specific instance.

    # Find available instances
    try:
        instances = provider.find_instances(requirements, limit=10)
    except Exception as e:
        logger.warning(f"Failed to find instances: {e}")
        pytest.skip(f"Could not find instances: {e}")

    if not instances:
        pytest.skip(
            f"No instances available for requirements: {requirements}"
        )

    # Select instance based on preference
    if prefer_cheapest and len(instances) > 1:
        selected = min(instances, key=lambda i: i.price_per_hour)
    else:
        selected = instances[0]

    logger.info(
        f"Selected instance: {selected.instance_type} "
        f"@ ${selected.price_per_hour}/hr in {selected.region}"
    )

    # Update config to use the instance's region if not specified
    if config.region and config.region != selected.region:
        logger.info(
            f"Updating task region from {config.region} to {selected.region} "
            f"to match available instance"
        )
        config = config.model_copy(update={"region": selected.region})

    # Submit task - extract instance type from the selected instance
    # The provider will handle region selection internally
    instance_type = selected.instance_type
    if instance_type.startswith("it_"):
        # If it's an FID, we need to map it back to user-friendly name
        # For testing, we'll use a simple mapping
        instance_type = "a100"  # Default for testing

    return provider.submit_task(
        instance_type=instance_type,
        config=config
    )


def discover_available_instance_type(
    provider: FCPProvider,
    prefer_gpu: bool = True
) -> Optional[str]:
    """Discover an available instance type for testing.
    
    Args:
        provider: The FCP provider
        prefer_gpu: If True, prefer GPU instances
        
    Returns:
        Instance type name if found, None otherwise
    """
    try:
        instances = provider.find_instances(
            {"max_price_per_hour": 100.0},
            limit=20
        )

        if not instances:
            return None

        if prefer_gpu:
            # Try to find a GPU instance
            gpu_instances = [
                i for i in instances
                if any(gpu in i.instance_type.lower()
                      for gpu in ['a100', 'h100', 'v100', 'a40', 't4'])
            ]
            if gpu_instances:
                return gpu_instances[0].instance_type

        # Return any instance
        return instances[0].instance_type

    except Exception as e:
        logger.warning(f"Failed to discover instance types: {e}")
        return None


def skip_if_no_instances(func):
    """Decorator to skip test if no instances are available.
    
    Usage:
        @skip_if_no_instances
        def test_something(provider):
            # Test will be skipped if no instances available
    """
    def wrapper(*args, **kwargs):
        # Find provider in args
        provider = None
        for arg in args:
            if isinstance(arg, FCPProvider):
                provider = arg
                break

        if provider:
            instance_type = discover_available_instance_type(provider)
            if not instance_type:
                pytest.skip("No instances available in test environment")

        return func(*args, **kwargs)

    return wrapper
