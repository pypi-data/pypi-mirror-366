"""Property-based test generators using Hypothesis.

These generators create test data for property-based testing,
helping find edge cases and ensure robustness.
"""

import string
from datetime import datetime, timedelta
from typing import Optional

try:
    from hypothesis import strategies as st
    from hypothesis import assume
except ImportError:
    raise ImportError(
        "Property-based testing requires hypothesis. "
        "Install with: pip install hypothesis"
    )

from flow.api.models import TaskConfig, VolumeSpec, StorageInterface


# ========== Basic Type Generators ==========

@st.composite
def valid_identifier(draw, prefix: str = "id") -> str:
    """Generate valid identifier strings."""
    suffix = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "-",
        min_size=4,
        max_size=16
    ))
    return f"{prefix}-{suffix}"


@st.composite
def valid_task_name(draw) -> str:
    """Generate valid task names."""
    prefix = draw(st.sampled_from([
        "train", "eval", "test", "process", 
        "analyze", "compute", "transform"
    ]))
    suffix = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + "-_",
        min_size=3,
        max_size=20
    ))
    return f"{prefix}-{suffix}"


# ========== Instance Type Generators ==========

@st.composite
def gpu_memory_size(draw) -> str:
    """Generate valid GPU memory sizes."""
    size = draw(st.sampled_from([16, 24, 32, 40, 48, 80]))
    return f"{size}gb"


@st.composite
def valid_gpu_type(draw) -> str:
    """Generate valid GPU instance types."""
    model = draw(st.sampled_from(["a100", "h100", "v100", "a10", "t4"]))
    memory = draw(gpu_memory_size())
    return f"{model}-{memory}"


@st.composite
def valid_cpu_type(draw) -> str:
    """Generate valid CPU instance types."""
    size = draw(st.sampled_from(["small", "medium", "large", "xlarge"]))
    return f"cpu-{size}"


@st.composite
def valid_instance_type(draw) -> str:
    """Generate any valid instance type."""
    return draw(st.one_of(
        valid_gpu_type(),
        valid_cpu_type()
    ))


# ========== Region Generators ==========

@st.composite
def valid_region(draw) -> str:
    """Generate valid cloud regions."""
    cloud = draw(st.sampled_from(["us", "eu", "ap"]))
    location = draw(st.sampled_from(["east", "west", "central", "north", "south"]))
    number = draw(st.integers(min_value=1, max_value=4))
    return f"{cloud}-{location}-{number}"


@st.composite
def valid_availability_zone(draw, region: Optional[str] = None) -> str:
    """Generate valid availability zone."""
    if region is None:
        region = draw(valid_region())
    suffix = draw(st.sampled_from(["a", "b", "c", "d"]))
    return f"{region}{suffix}"


# ========== Price Generators ==========

@st.composite
def reasonable_price(draw) -> float:
    """Generate reasonable hourly prices for instances."""
    # Use realistic price ranges
    base_price = draw(st.floats(min_value=0.1, max_value=50.0))
    # Round to 2 decimal places like real prices
    return round(base_price, 2)


@st.composite
def price_string(draw) -> str:
    """Generate price as string (how API returns it)."""
    price = draw(reasonable_price())
    return f"${price:.2f}"


# ========== Command/Script Generators ==========

@st.composite
def valid_command(draw) -> str:
    """Generate valid shell commands."""
    commands = [
        "python train.py",
        "python -m model.train",
        "bash run.sh",
        "jupyter notebook",
        "./scripts/process.sh",
        "make train",
        "nvidia-smi",
        "echo 'test'",
        "sleep 10",
    ]
    base_cmd = draw(st.sampled_from(commands))
    
    # Sometimes add arguments
    if draw(st.booleans()):
        args = draw(st.lists(
            st.text(
                alphabet=string.ascii_letters + string.digits + "-_",
                min_size=1,
                max_size=10
            ),
            min_size=1,
            max_size=3
        ))
        return f"{base_cmd} {' '.join(args)}"
    
    return base_cmd


@st.composite
def valid_script(draw) -> str:
    """Generate valid shell scripts."""
    lines = draw(st.lists(
        valid_command(),
        min_size=1,
        max_size=5
    ))
    return "\n".join(lines)


# ========== Volume Generators ==========

@st.composite
def volume_size(draw) -> int:
    """Generate reasonable volume sizes in GB."""
    # Common sizes
    common = [10, 50, 100, 200, 500, 1000]
    if draw(st.booleans(p=0.7)):
        return draw(st.sampled_from(common))
    # Or any reasonable size
    return draw(st.integers(min_value=1, max_value=2000))


@st.composite
def mount_path(draw) -> str:
    """Generate valid mount paths."""
    paths = ["/data", "/models", "/outputs", "/scratch", "/workspace"]
    base = draw(st.sampled_from(paths))
    
    # Sometimes add subdirectory
    if draw(st.booleans(p=0.3)):
        subdir = draw(st.text(
            alphabet=string.ascii_lowercase + string.digits,
            min_size=1,
            max_size=10
        ))
        return f"{base}/{subdir}"
    
    return base


@st.composite
def volume_spec(draw) -> VolumeSpec:
    """Generate valid volume specifications."""
    return VolumeSpec(
        mount_path=draw(mount_path()),
        size_gb=draw(volume_size())
    )


# ========== Task Config Generators ==========

@st.composite
def task_config(draw) -> TaskConfig:
    """Generate valid task configurations with all fields."""
    # Must have either command or script
    has_command = draw(st.booleans())
    
    config = TaskConfig(
        name=draw(valid_task_name()),
        instance_type=draw(valid_instance_type()),
        command=draw(valid_command()) if has_command else "",
        command=draw(valid_script()) if not has_command else "",
        num_instances=draw(st.integers(min_value=1, max_value=4)),
        max_price_per_hour=draw(reasonable_price()),
        region=draw(valid_region()),
        volumes=draw(st.lists(volume_spec(), min_size=0, max_size=3))
    )
    
    # Ensure valid
    assume(config.command or config.command)
    assume(config.max_price_per_hour > 0)
    
    return config


# ========== Time Generators ==========

@st.composite  
def past_datetime(draw, max_days_ago: int = 30) -> datetime:
    """Generate datetime in the past."""
    days_ago = draw(st.integers(min_value=0, max_value=max_days_ago))
    hours_ago = draw(st.integers(min_value=0, max_value=23))
    return datetime.now() - timedelta(days=days_ago, hours=hours_ago)


@st.composite
def duration_hours(draw, max_hours: int = 24) -> float:
    """Generate reasonable task durations in hours."""
    # Most tasks are short
    if draw(st.booleans(p=0.7)):
        return draw(st.floats(min_value=0.1, max_value=2.0))
    # Some run longer
    return draw(st.floats(min_value=2.0, max_value=float(max_hours)))


# ========== Error Generators ==========

@st.composite
def api_error_response(draw) -> dict:
    """Generate API error response structures."""
    error_types = [
        ("INVALID_REQUEST", 400),
        ("UNAUTHORIZED", 401), 
        ("FORBIDDEN", 403),
        ("NOT_FOUND", 404),
        ("QUOTA_EXCEEDED", 429),
        ("SERVER_ERROR", 500),
        ("SERVICE_UNAVAILABLE", 503),
    ]
    
    error_type, status_code = draw(st.sampled_from(error_types))
    
    return {
        "error": error_type,
        "message": draw(st.text(min_size=10, max_size=100)),
        "status_code": status_code,
        "request_id": draw(valid_identifier("req"))
    }


# ========== Network Condition Generators ==========

@st.composite
def network_latency(draw) -> float:
    """Generate realistic network latencies in seconds."""
    # Most requests are fast
    if draw(st.booleans(p=0.8)):
        return draw(st.floats(min_value=0.01, max_value=0.5))
    # Some are slow
    return draw(st.floats(min_value=0.5, max_value=5.0))


@st.composite
def retry_scenario(draw) -> list:
    """Generate retry scenarios for testing resilience."""
    num_failures = draw(st.integers(min_value=0, max_value=5))
    
    scenario = []
    for i in range(num_failures):
        # Transient errors that should be retried
        error = draw(st.sampled_from([
            ConnectionError("Connection reset"),
            TimeoutError("Request timeout"),
            APIError("Service temporarily unavailable", status_code=503),
        ]))
        scenario.append(("error", error))
    
    # Finally succeed
    scenario.append(("success", None))
    
    return scenario