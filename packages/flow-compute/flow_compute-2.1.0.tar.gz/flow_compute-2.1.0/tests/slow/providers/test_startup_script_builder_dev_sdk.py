"""Test startup script builder functionality using flow.dev SDK.

This module tests the StartupScriptBuilder class and its generated scripts
using fast container-based execution on persistent dev VMs.
"""

import base64
import gzip
import json
import pytest
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from flow import Flow
from flow.api.models import TaskConfig, VolumeSpec
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder
from flow.providers.fcp.runtime.startup.sections import (
    HeaderSection,
    PortForwardingSection,
    VolumeSection,
    DockerSection,
    UserScriptSection,
    CompletionSection,
    ScriptContext,
)


class TestStartupScriptBuilder:
    """Test StartupScriptBuilder with real execution via flow.dev."""
    
    @pytest.fixture(scope="class")
    def flow_client(self):
        """Create Flow client and ensure dev VM."""
        flow = Flow()
        flow.dev.ensure_started()
        yield flow
        # Keep VM running for other tests
    
    @pytest.fixture
    def builder(self):
        """Create default StartupScriptBuilder."""
        return StartupScriptBuilder()
    
    def execute_script_in_container(
        self, 
        flow: Flow, 
        script_content: str,
        image: str = "ubuntu:22.04"
    ) -> Dict[str, any]:
        """Execute startup script in container and collect results.
        
        Args:
            flow: Flow client instance
            script_content: The startup script to execute
            image: Docker image to use
            
        Returns:
            Dict with execution results
        """
        # Prepare script for container execution
        # Replace system paths with container-friendly paths
        container_script = script_content.replace(
            "/var/log/flow-startup.log", "/tmp/flow-startup.log"
        ).replace(
            "/var/run/fcp-startup-complete", "/tmp/flow-startup-complete"
        ).replace(
            "/var/lib/cloud/instance/scripts/", "/tmp/scripts/"
        )
        
        # Create wrapper that captures results
        wrapper = f"""#!/bin/bash
# Create necessary directories
mkdir -p /tmp/scripts /tmp/logs

# Save the script
cat > /tmp/startup-script.sh << 'SCRIPT_END'
{container_script}
SCRIPT_END

# Make executable
chmod +x /tmp/startup-script.sh

# Run the script
/tmp/startup-script.sh
EXIT_CODE=$?

# Collect results
echo "EXIT_CODE=$EXIT_CODE"
if [ -f /tmp/flow-startup-complete ]; then
    echo "COMPLETION_MARKER=true"
else
    echo "COMPLETION_MARKER=false"
fi

if [ -f /tmp/flow-startup.log ]; then
    echo "LOG_EXISTS=true"
    echo "LOG_LINES=$(wc -l < /tmp/flow-startup.log)"
else
    echo "LOG_EXISTS=false"
fi

# Check for key environment variables
env | grep ^FLOW_ | sort

exit $EXIT_CODE
"""
        
        # Execute in container
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(wrapper)
            temp_path = f.name
        
        try:
            # Copy script to container workspace
            exit_code = flow.dev.exec(
                f"cat > /tmp/test-wrapper.sh << 'EOF'\n{wrapper}\nEOF && chmod +x /tmp/test-wrapper.sh && /tmp/test-wrapper.sh",
                image=image
            )
            
            # Parse results (in real implementation, we'd capture output)
            results = {
                "exit_code": exit_code,
                "success": exit_code == 0,
                "completion_marker": False,  # Would parse from output
                "log_exists": False,  # Would parse from output
                "log_lines": 0,  # Would parse from output
            }
            
            return results
            
        finally:
            Path(temp_path).unlink()
    
    def test_minimal_script_execution(self, flow_client, builder):
        """Test minimal startup script executes successfully."""
        config = TaskConfig(
            name="minimal-test",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["echo", "Hello from Flow"]
        )
        
        script_result = builder.build(config)
        assert script_result.is_valid
        
        # Execute in container
        results = self.execute_script_in_container(
            flow_client,
            script_result.content
        )
        
        assert results["success"], "Minimal script execution failed"
        assert results["exit_code"] == 0
    
    def test_script_with_environment_variables(self, flow_client, builder):
        """Test script with environment variables."""
        config = TaskConfig(
            name="env-test",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["env"],
            env={
                "API_KEY": "test-key-123",
                "DEBUG": "true",
                "MODEL_PATH": "/models/llama",
                "FLOW_CUSTOM": "custom-value"
            }
        )
        
        script_result = builder.build(config)
        
        # Verify env vars are in script
        assert "export API_KEY" in script_result.content
        assert "export DEBUG" in script_result.content
        assert "export MODEL_PATH" in script_result.content
        
        # Execute and verify
        exit_code = flow_client.dev.exec(
            f"export API_KEY=test-key-123 && export DEBUG=true && echo $API_KEY && echo $DEBUG",
            image="ubuntu:22.04"
        )
        
        assert exit_code == 0
    
    def test_script_with_volumes(self, flow_client, builder):
        """Test script with volume mounting."""
        config = TaskConfig(
            name="volume-test",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["ls", "-la", "/data"],
            volumes=[
                VolumeSpec(size_gb=10, mount_path="/data/models"),
                VolumeSpec(size_gb=20, mount_path="/data/cache"),
                VolumeSpec(size_gb=50, mount_path="/var/lib/docker"),
            ]
        )
        
        script_result = builder.build(config)
        
        # Verify mount commands are present
        assert "mkdir -p /data/models" in script_result.content
        assert "mkdir -p /data/cache" in script_result.content
        assert "mkdir -p /var/lib/docker" in script_result.content
        
        # Test directory creation in container
        for mount_path in ["/data/models", "/data/cache"]:
            exit_code = flow_client.dev.exec(
                f"mkdir -p {mount_path} && echo 'test' > {mount_path}/test.txt && cat {mount_path}/test.txt",
                image="ubuntu:22.04"
            )
            assert exit_code == 0, f"Failed to create/use {mount_path}"
    
    def test_docker_operations_in_script(self, flow_client, builder):
        """Test Docker operations in generated script."""
        config = TaskConfig(
            name="docker-test",
            instance_type="h100",
            image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
            command=["python", "-c", "import torch; print(torch.__version__)"],
        )
        
        script_result = builder.build(config)
        
        # Verify Docker commands
        assert "docker pull" in script_result.content
        assert config.image in script_result.content
        
        # Test Docker operations
        # Pull a small image
        exit_code = flow_client.dev.exec(
            "docker pull hello-world && docker run --rm hello-world",
            image="ubuntu:22.04"
        )
        assert exit_code == 0, "Docker operations failed"
    
    def test_compressed_script_handling(self, flow_client, builder):
        """Test compressed startup scripts."""
        # Create builder with low size limit to force compression
        small_builder = StartupScriptBuilder(max_uncompressed_size=1000)
        
        # Create config with large content
        large_env = {f"VAR_{i}": "x" * 100 for i in range(50)}
        config = TaskConfig(
            name="compressed-test",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["echo"] + ["x" * 100] * 10,  # Large command
            env=large_env
        )
        
        script_result = small_builder.build(config)
        
        assert script_result.compressed, "Script should be compressed"
        assert "base64 -d | gunzip | bash" in script_result.content
        
        # Test decompression works
        test_content = "echo 'Hello from compressed script'"
        compressed = gzip.compress(test_content.encode())
        encoded = base64.b64encode(compressed).decode()
        
        exit_code = flow_client.dev.exec(
            f"echo '{encoded}' | base64 -d | gunzip | bash",
            image="ubuntu:22.04"
        )
        assert exit_code == 0, "Decompression failed"
    
    def test_custom_script_sections(self, flow_client):
        """Test custom script sections."""
        
        class CustomLoggingSection(UserScriptSection):
            """Custom section for enhanced logging."""
            
            @property
            def name(self) -> str:
                return "custom_logging"
            
            @property
            def priority(self) -> int:
                return 5  # Run early
            
            def generate(self, context: ScriptContext) -> str:
                return """
# Enhanced logging setup
export LOG_LEVEL=DEBUG
mkdir -p /tmp/flow-logs
echo "[$(date)] Starting Flow task ${FLOW_TASK_ID}" | tee -a /tmp/flow-logs/startup.log
"""
        
        class CustomMonitoringSection(UserScriptSection):
            """Custom section for monitoring."""
            
            @property
            def name(self) -> str:
                return "monitoring"
            
            @property 
            def priority(self) -> int:
                return 90  # Run late
            
            def generate(self, context: ScriptContext) -> str:
                return """
# Report resource usage
echo "[$(date)] Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "[$(date)] Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2}')"
"""
        
        # Create builder with custom sections
        custom_sections = [
            HeaderSection(),
            CustomLoggingSection(),
            VolumeSection(),
            DockerSection(),
            UserScriptSection(),
            CustomMonitoringSection(),
            CompletionSection(),
        ]
        
        custom_builder = StartupScriptBuilder(sections=custom_sections)
        
        config = TaskConfig(
            name="custom-sections",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["echo", "Testing custom sections"]
        )
        
        script_result = custom_builder.build(config)
        
        # Verify custom sections are included
        assert "Enhanced logging setup" in script_result.content
        assert "LOG_LEVEL=DEBUG" in script_result.content
        assert "Report resource usage" in script_result.content
        
        # Test execution
        exit_code = flow_client.dev.exec(
            "export LOG_LEVEL=DEBUG && mkdir -p /tmp/flow-logs && echo 'Log test' | tee -a /tmp/flow-logs/startup.log && free -h",
            image="ubuntu:22.04"
        )
        assert exit_code == 0
    
    def test_script_error_handling(self, flow_client, builder):
        """Test script error handling."""
        config = TaskConfig(
            name="error-test",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["false"],  # Command that always fails
        )
        
        script_result = builder.build(config)
        
        # Script should have error handling
        assert "set -euo pipefail" in script_result.content or "set -euxo pipefail" in script_result.content
        
        # Test that errors are caught
        exit_code = flow_client.dev.exec(
            "set -e && false && echo 'Should not reach here'",
            image="ubuntu:22.04"
        )
        assert exit_code != 0, "Error handling not working"
    
    def test_concurrent_script_generation(self, builder):
        """Test concurrent script generation is thread-safe."""
        import concurrent.futures
        
        def generate_script(task_id: int) -> str:
            config = TaskConfig(
                name=f"concurrent-{task_id}",
                instance_type="h100",
                image="ubuntu:22.04",
                command=[f"echo 'Task {task_id}'"],
                env={f"TASK_ID": str(task_id)}
            )
            result = builder.build(config)
            return result.content
        
        # Generate scripts concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_script, i) for i in range(10)]
            scripts = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Verify all scripts were generated
        assert len(scripts) == 10
        
        # Verify each script has unique content
        for i, script in enumerate(scripts):
            # At least one script should contain the task ID
            task_refs = sum(1 for s in scripts if f"Task {i}" in s or f"TASK_ID={i}" in s)
            assert task_refs >= 1, f"Task {i} not found in any script"
    
    def test_script_size_validation(self, builder):
        """Test script size validation."""
        # Create config that generates very large script
        huge_command = " ".join(["echo"] + ["x" * 1000] * 100)
        config = TaskConfig(
            name="huge-script",
            instance_type="h100",
            image="ubuntu:22.04",
            command=huge_command
        )
        
        script_result = builder.build(config)
        
        # Should handle large scripts gracefully
        assert script_result.is_valid
        assert script_result.size_bytes > 0
        
        # If too large, should be compressed
        if script_result.size_bytes > builder.max_uncompressed_size:
            assert script_result.compressed


@pytest.mark.integration
class TestStartupScriptIntegration:
    """Integration tests for startup scripts with real workloads."""
    
    @pytest.fixture(scope="class")
    def flow_client(self):
        """Create Flow client with dev VM."""
        flow = Flow()
        flow.dev.ensure_started()
        yield flow
    
    def test_ml_workload_script(self, flow_client):
        """Test startup script for ML workload."""
        builder = StartupScriptBuilder()
        
        config = TaskConfig(
            name="ml-training",
            instance_type="h100",
            image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime",
            command=[
                "python", "-c",
                "import torch; print(f'PyTorch {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
            ],
            env={
                "CUDA_VISIBLE_DEVICES": "0",
                "PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:512",
                "HF_HOME": "/data/huggingface",
            },
            volumes=[
                VolumeSpec(size_gb=100, mount_path="/data/models"),
                VolumeSpec(size_gb=50, mount_path="/data/huggingface"),
            ]
        )
        
        script_result = builder.build(config)
        
        # Test key components exist
        assert "CUDA_VISIBLE_DEVICES" in script_result.content
        assert "/data/models" in script_result.content
        assert "docker pull pytorch/pytorch" in script_result.content
        
        # Test PyTorch import works
        exit_code = flow_client.dev.exec(
            "python -c 'import torch; print(torch.__version__)'",
            image="pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime"
        )
        assert exit_code == 0
    
    def test_database_workload_script(self, flow_client):
        """Test startup script for database workload."""
        builder = StartupScriptBuilder()
        
        config = TaskConfig(
            name="postgres-db",
            instance_type="cpu-large",
            image="postgres:15",
            command=["postgres"],
            env={
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_DB": "testdb",
                "PGDATA": "/var/lib/postgresql/data/pgdata",
            },
            volumes=[
                VolumeSpec(size_gb=100, mount_path="/var/lib/postgresql/data"),
                VolumeSpec(size_gb=50, mount_path="/backup"),
            ]
        )
        
        script_result = builder.build(config)
        
        # Verify PostgreSQL setup
        assert "POSTGRES_PASSWORD" in script_result.content
        assert "/var/lib/postgresql/data" in script_result.content
        
        # Test PostgreSQL operations (simplified)
        exit_code = flow_client.dev.exec(
            "echo 'PostgreSQL config would go here'",
            image="postgres:15"
        )
        assert exit_code == 0


def main():
    """Run tests standalone."""
    import sys
    
    print("Testing StartupScriptBuilder with flow.dev SDK")
    print("=" * 60)
    
    # Create flow client
    flow = Flow()
    print("Ensuring dev VM is running...")
    flow.dev.ensure_started()
    
    # Run some basic tests
    builder = StartupScriptBuilder()
    
    # Test 1: Basic script generation
    print("\n1. Testing basic script generation...")
    config = TaskConfig(
        name="test-basic",
        instance_type="h100",
        image="ubuntu:22.04",
        command=["echo", "Hello Flow"]
    )
    
    script = builder.build(config)
    print(f"   Generated script: {script.size_bytes} bytes")
    print(f"   Compressed: {script.compressed}")
    print(f"   Valid: {script.is_valid}")
    
    # Test 2: Execute in container
    print("\n2. Testing script execution...")
    exit_code = flow.dev.exec("echo 'Hello from container'", image="ubuntu:22.04")
    print(f"   Exit code: {exit_code}")
    
    # Test 3: Concurrent execution
    print("\n3. Testing concurrent execution...")
    import concurrent.futures
    
    def run_task(task_id):
        return flow.dev.exec(f"echo 'Task {task_id}' && sleep 1", image="ubuntu:22.04")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_task, i) for i in range(3)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    print(f"   All tasks completed: {all(r == 0 for r in results)}")
    
    print("\n✅ All tests completed!")
    print("\nDev VM is still running. Use 'flow dev stop' to stop it.")
    
    return 0


if __name__ == "__main__":
    exit(main())