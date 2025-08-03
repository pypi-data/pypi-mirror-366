#!/usr/bin/env python3
"""Test the SLURM adapter functionality."""

import asyncio
import sys
from pathlib import Path

from flow._internal.frontends.slurm.adapter import SlurmFrontendAdapter
from flow import Flow
from flow.api.models import TaskStatus


async def test_slurm_adapter():
    """Test running a SLURM script through the adapter."""
    
    # Path to our SLURM script
    slurm_script = Path("examples/01_basics/gpu_test_slurm.sh")
    
    if not slurm_script.exists():
        print(f"Error: SLURM script not found at {slurm_script}")
        return 1
    
    print(f"Testing SLURM adapter with script: {slurm_script}")
    
    # Create SLURM adapter
    adapter = SlurmFrontendAdapter()
    
    try:
        # Parse SLURM script into TaskConfig
        print("\n1. Parsing SLURM script...")
        task_config = await adapter.parse_and_convert(slurm_script)
        
        print(f"\nParsed task config:")
        print(f"  Name: {task_config.name}")
        print(f"  Instance type: {task_config.instance_type}")
        print(f"  Nodes: {task_config.num_instances}")
        print(f"  Max runtime: {task_config.max_run_time_hours} hours")
        print(f"  Environment variables: {len(task_config.env)} set")
        
        # Submit task using Flow
        print("\n2. Submitting task to Flow...")
        with Flow() as flow_client:
            task = flow_client.run(task_config)
            print(f"Task submitted with ID: {task.task_id}")
            
            # Stream logs
            print("\n3. Streaming task logs...")
            print("-" * 60)
            try:
                for line in task.logs(follow=True):
                    print(line, end="")
            except KeyboardInterrupt:
                print("\n\nLog streaming interrupted.")
            
            # Wait for completion
            print("\n4. Waiting for task completion...")
            task.wait()
            
            # Check final status
            if task.status == TaskStatus.COMPLETED:
                print("\n✓ Task completed successfully!")
                return 0
            else:
                print(f"\n✗ Task failed with status: {task.status}")
                return 1
                
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(test_slurm_adapter()))