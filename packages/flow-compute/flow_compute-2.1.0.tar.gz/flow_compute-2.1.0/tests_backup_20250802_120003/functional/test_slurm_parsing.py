#!/usr/bin/env python3
"""Test SLURM script parsing without submission."""

import asyncio
import sys
from pathlib import Path

from flow._internal.frontends.slurm.adapter import SlurmFrontendAdapter


async def test_slurm_parsing():
    """Test parsing various SLURM scripts."""
    
    # Test our GPU verification script
    slurm_script = Path("examples/01_basics/gpu_test_slurm.sh")
    
    if not slurm_script.exists():
        print(f"Error: SLURM script not found at {slurm_script}")
        return 1
    
    print(f"Testing SLURM adapter parsing with: {slurm_script}")
    
    # Create SLURM adapter
    adapter = SlurmFrontendAdapter()
    
    try:
        # Parse SLURM script
        print("\nParsing SLURM script...")
        task_config = await adapter.parse_and_convert(slurm_script)
        
        print(f"\nParsed Configuration:")
        print(f"  Job Name: {task_config.name}")
        print(f"  Instance Type: {task_config.instance_type}")
        print(f"  Number of Nodes: {task_config.num_instances}")
        print(f"  Max Runtime: {task_config.max_run_time_hours} hours")
        print(f"  Max Price/Hour: ${task_config.max_price_per_hour}")
        print(f"  Image: {task_config.image}")
        
        print(f"\nEnvironment Variables:")
        for key, value in sorted(task_config.env.items()):
            print(f"  {key}={value}")
        
        print(f"\nCommand Preview (first 500 chars):")
        print("-" * 60)
        print(task_config.command[:500] + "..." if len(task_config.command) > 500 else task_config.command)
        
        # Test array job parsing
        print("\n\nTesting Array Job Parsing...")
        array_configs = await adapter.parse_array_job(
            slurm_script,
            array="1-5"  # Override to create array job
        )
        
        print(f"Array job would create {len(array_configs)} tasks:")
        for i, config in enumerate(array_configs):
            print(f"  Task {i+1}: {config.name} (SLURM_ARRAY_TASK_ID={config.env['SLURM_ARRAY_TASK_ID']})")
        
        # Test with CLI overrides
        print("\n\nTesting with CLI overrides...")
        override_config = await adapter.parse_and_convert(
            slurm_script,
            job_name="custom-gpu-test",
            gpus="a100:4",  
            time="24:00:00"
        )
        
        print(f"Overridden Configuration:")
        print(f"  Job Name: {override_config.name} (overridden)")
        print(f"  Instance Type: {override_config.instance_type} (overridden)")
        print(f"  Max Runtime: {override_config.max_run_time_hours} hours (overridden)")
        
        return 0
        
    except Exception as e:
        print(f"\nError during parsing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(test_slurm_parsing()))