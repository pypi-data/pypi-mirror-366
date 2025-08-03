"""GPU execution test - only runs on releases.

This is the ONE test that actually waits for an instance.
"""

import os

import pytest

from flow import Flow
from flow.api.models import TaskConfig


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(not os.getenv("RUN_RELEASE_TEST"), reason="Set RUN_RELEASE_TEST=1 to run")
def test_gpu_execution():
    """Actually provision and run on GPU - takes 15+ minutes."""
    flow = Flow()

    config = TaskConfig(
        name="release-gpu-test",
        instance_type="a100",
        command="""
            # Verify GPU is accessible
            nvidia-smi
            
            # Run a simple GPU operation
            python3 -c "
import torch
if torch.cuda.is_available():
    print(f'GPU available: {torch.cuda.get_device_name(0)}')
    # Simple computation to verify it works
    x = torch.randn(1000, 1000).cuda()
    y = torch.matmul(x, x)
    print('GPU computation successful')
else:
    print('ERROR: No GPU found')
    exit(1)
"
            echo "TEST PASSED"
        """,
        max_price_per_hour=50.0,
        max_run_time_hours=0.5,  # 30 minutes max
    )

    # This will take 15+ minutes
    task = flow.run(config, wait=True)

    # Verify it worked
    assert task.status.value == "completed"
    logs = task.logs()
    assert "GPU available" in logs
    assert "GPU computation successful" in logs
    assert "TEST PASSED" in logs
