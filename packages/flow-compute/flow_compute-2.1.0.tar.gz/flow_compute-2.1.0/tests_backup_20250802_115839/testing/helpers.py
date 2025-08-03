"""Test helpers for integration and E2E tests."""

from typing import Optional

from flow.api.models import TaskConfig
from flow.providers.fcp.provider import FCPProvider


def get_available_instance_for_test(
    provider: FCPProvider,
    max_price: float = 10.0,
    region: Optional[str] = None
) -> Optional[str]:
    """Get an available instance type for testing.
    
    Since the API returns opaque instance IDs without hardware info,
    this helper finds any available instance within the price range.
    
    Args:
        provider: The FCP provider instance
        max_price: Maximum price per hour
        region: Preferred region (optional)
        
    Returns:
        Instance type ID if found, None otherwise
    """
    requirements = {"max_price_per_hour": max_price}
    if region:
        requirements["region"] = region

    instances = provider.find_instances(requirements, limit=10)

    if instances:
        # Sort by price and return cheapest
        sorted_instances = sorted(instances, key=lambda x: x.price_per_hour)
        return sorted_instances[0].instance_type

    return None


def create_test_config_with_available_instance(
    provider: FCPProvider,
    name: str,
    command: str = "echo 'test'",
    max_price: float = 10.0,
    **kwargs
) -> TaskConfig:
    """Create a TaskConfig with an available instance type.
    
    This helper ensures tests use actual available instances from the API.
    
    Args:
        provider: The FCP provider instance
        name: Task name
        command: Command to run
        max_price: Maximum price per hour
        **kwargs: Additional TaskConfig parameters
        
    Returns:
        TaskConfig with a valid instance type
        
    Raises:
        RuntimeError: If no instances are available
    """
    instance_type = get_available_instance_for_test(provider, max_price)

    if not instance_type:
        raise RuntimeError(
            f"No instances available under ${max_price}/hour. "
            "Check API connectivity and instance availability."
        )

    config_data = {
        "name": name,
        "command": command,
        "instance_type": instance_type,
        "max_price_per_hour": max_price,
        **kwargs
    }

    return TaskConfig(**config_data)
