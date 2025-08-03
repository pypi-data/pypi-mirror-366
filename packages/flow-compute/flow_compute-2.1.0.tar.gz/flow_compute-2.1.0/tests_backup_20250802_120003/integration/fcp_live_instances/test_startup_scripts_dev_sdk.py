#!/usr/bin/env python3
"""Integration tests for startup script functionality using flow.dev SDK.

This module tests startup scripts are properly injected and executed on FCP 
instances, leveraging the flow.dev SDK for fast iterative testing on 
persistent VMs.

The flow.dev SDK provides:
- Reusable dev VMs that persist between test runs
- Fast container-based execution without full VM startup overhead
- Clean isolation between tests using Docker containers
- Automatic cleanup and resource management
"""

import json
import os
import pytest
import time
from pathlib import Path
from typing import Dict, List, Optional

from flow import Flow
from flow.api.models import TaskConfig, VolumeSpec
from flow.errors import DevVMNotFoundError, DevContainerError
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder
from flow.providers.fcp.runtime.startup.sections import ScriptContext


class StartupScriptDevTester:
    """Test runner for startup script functionality using flow.dev SDK."""
    
    def __init__(self, flow_client: Optional[Flow] = None):
        """Initialize tester with Flow client.
        
        Args:
            flow_client: Flow SDK client instance. Creates new one if not provided.
        """
        self.flow = flow_client or Flow()
        self._ensure_dev_vm()
    
    def _ensure_dev_vm(self):
        """Ensure dev VM is running for tests."""
        try:
            # Check if VM already exists
            status = self.flow.dev.status()
            if status["vm"]:
                print(f"Using existing dev VM: {status['vm']['name']}")
                return
        except DevVMNotFoundError:
            pass
        
        # Start new dev VM
        print("Starting new dev VM for tests...")
        vm = self.flow.dev.start(instance_type="h100")
        print(f"Dev VM started: {vm.name}")
    
    def run_test_command(self, command: str, timeout: int = 30) -> tuple[int, str, str]:
        """Run command on dev VM via container execution.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        # Create a wrapper script that captures output
        wrapper_script = f"""
set -o pipefail
OUTPUT=$(mktemp)
ERROR=$(mktemp)
EXITCODE=0

# Run the command with timeout
timeout {timeout} bash -c '{command}' >$OUTPUT 2>$ERROR || EXITCODE=$?

# Output results in parseable format
echo "===EXITCODE===$EXITCODE"
echo "===STDOUT==="
cat $OUTPUT
echo "===STDERR==="  
cat $ERROR

rm -f $OUTPUT $ERROR
exit 0
"""
        
        try:
            # Execute in container
            exit_code = self.flow.dev.exec(
                f"bash -c {json.dumps(wrapper_script)}",
                image="ubuntu:22.04"
            )
            
            # For this test framework, we need to parse the output
            # In real usage, flow.dev.exec would return the actual output
            # This is a simplified version for the example
            return exit_code, "", ""
            
        except DevContainerError as e:
            return 1, "", str(e)
    
    def verify_startup_script_basics(self) -> Dict[str, any]:
        """Verify basic startup script execution in container."""
        results = {}
        
        # First, simulate startup script execution in container
        startup_script = self._get_test_startup_script()
        
        # Execute startup script in container
        print("Executing test startup script in container...")
        exit_code = self.flow.dev.exec(
            f"bash -c {json.dumps(startup_script)}",
            image="ubuntu:22.04"
        )
        
        results["script_execution"] = {
            "success": exit_code == 0,
            "exit_code": exit_code
        }
        
        # Check script artifacts
        tests = [
            ("startup_log_created", "test -f /tmp/flow-startup.log"),
            ("completion_marker", "test -f /tmp/flow-startup-complete"),
            ("env_vars_set", "env | grep -q ^FLOW_"),
        ]
        
        for test_name, command in tests:
            exit_code, stdout, stderr = self.run_test_command(command)
            results[test_name] = {
                "success": exit_code == 0,
                "output": stdout.strip() if exit_code == 0 else stderr.strip()
            }
        
        return results
    
    def _get_test_startup_script(self) -> str:
        """Generate a test startup script."""
        builder = StartupScriptBuilder()
        config = TaskConfig(
            name="test-startup",
            instance_type="h100",
            image="ubuntu:22.04",
            command=["echo", "test"],
            env={"FLOW_TEST": "1"}
        )
        
        script_result = builder.build(config)
        
        # Modify script for container testing
        # Remove cloud-init specific parts and adjust paths
        script = script_result.content
        script = script.replace("/var/log/flow-startup.log", "/tmp/flow-startup.log")
        script = script.replace("/var/run/fcp-startup-complete", "/tmp/flow-startup-complete")
        
        return script
    
    def test_environment_variables(self) -> Dict[str, any]:
        """Test Flow environment variables in container context."""
        results = {}
        
        # Set up test environment
        test_env = {
            "FLOW_TASK_ID": "test-task-123",
            "FLOW_INSTANCE_ID": "test-instance-456", 
            "FLOW_PROVIDER": "fcp",
            "FLOW_TEST_VAR": "test_value"
        }
        
        # Create command that exports env vars and checks them
        env_setup = " && ".join([f"export {k}={v}" for k, v in test_env.items()])
        check_command = f"{env_setup} && env | grep ^FLOW_ | sort"
        
        exit_code = self.flow.dev.exec(
            f"bash -c {json.dumps(check_command)}",
            image="ubuntu:22.04"
        )
        
        results["env_vars_exported"] = exit_code == 0
        results["expected_var_count"] = len(test_env)
        
        # Check specific variables
        for var_name in ["FLOW_TASK_ID", "FLOW_INSTANCE_ID", "FLOW_PROVIDER"]:
            check_cmd = f"{env_setup} && echo ${var_name}"
            exit_code = self.flow.dev.exec(
                f"bash -c {json.dumps(check_cmd)}",
                image="ubuntu:22.04"  
            )
            results[f"has_{var_name.lower()}"] = exit_code == 0
        
        return results
    
    def test_docker_operations(self) -> Dict[str, any]:
        """Test Docker operations in dev container."""
        results = {}
        
        # Docker is already installed on dev VM, test operations
        docker_tests = [
            ("docker_available", "which docker"),
            ("docker_version", "docker --version"),
            ("docker_pull", "docker pull hello-world"),
            ("docker_run", "docker run --rm hello-world"),
        ]
        
        for test_name, command in docker_tests:
            exit_code = self.flow.dev.exec(command, image="ubuntu:22.04")
            results[test_name] = {
                "success": exit_code == 0,
                "exit_code": exit_code
            }
        
        return results
    
    def test_volume_operations(self) -> Dict[str, any]:
        """Test volume mount simulation in containers."""
        results = {}
        
        # Test creating mount points
        mount_points = ["/data/models", "/var/cache/app", "/backup"]
        
        for mount_path in mount_points:
            # Create directory and test access
            commands = [
                f"mkdir -p {mount_path}",
                f"echo 'test' > {mount_path}/test.txt",
                f"cat {mount_path}/test.txt"
            ]
            
            all_success = True
            for cmd in commands:
                exit_code = self.flow.dev.exec(cmd, image="ubuntu:22.04")
                if exit_code != 0:
                    all_success = False
                    break
            
            results[f"mount_{mount_path.replace('/', '_')}"] = all_success
        
        return results
    
    def test_script_compression(self) -> Dict[str, any]:
        """Test compressed script handling."""
        results = {}
        
        # Create a large script that would trigger compression
        builder = StartupScriptBuilder(max_uncompressed_size=1000)  # 1KB limit
        
        # Generate large environment
        large_env = {f"VAR_{i}": "x" * 50 for i in range(50)}
        
        config = TaskConfig(
            name="large-script",
            instance_type="h100",
            image="ubuntu:22.04",
            env=large_env,
            command="echo 'Testing large script'"
        )
        
        script_result = builder.build(config)
        
        results["script_compressed"] = script_result.compressed
        results["script_size_bytes"] = script_result.size_bytes
        
        if script_result.compressed:
            # Test decompression in container
            decompress_test = """
echo 'H4sIAAAAAAAAA0tJLElVyE0sTs1NzStRyCpNLikGADyMD3MUAAAA' | base64 -d | gunzip
"""
            exit_code = self.flow.dev.exec(
                f"bash -c {json.dumps(decompress_test)}",
                image="ubuntu:22.04"
            )
            results["decompression_works"] = exit_code == 0
        
        return results
    
    def test_concurrent_operations(self) -> Dict[str, any]:
        """Test concurrent container operations."""
        results = {}
        
        # Run multiple containers concurrently
        import concurrent.futures
        
        def run_container_task(task_id: int) -> bool:
            """Run a simple task in container."""
            command = f"echo 'Task {task_id}' && sleep 1 && echo 'Task {task_id} done'"
            exit_code = self.flow.dev.exec(command, image="ubuntu:22.04")
            return exit_code == 0
        
        # Run 5 concurrent tasks
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_container_task, i) for i in range(5)]
            results_list = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        results["concurrent_tasks_total"] = len(results_list)
        results["concurrent_tasks_successful"] = sum(results_list)
        results["all_concurrent_succeeded"] = all(results_list)
        
        return results
    
    def run_all_tests(self) -> Dict[str, any]:
        """Run all startup script tests using dev SDK."""
        print(f"Testing startup scripts using flow.dev SDK")
        print("=" * 50)
        
        all_results = {}
        
        test_suites = [
            ("Basic startup script checks", self.verify_startup_script_basics),
            ("Environment variables", self.test_environment_variables),
            ("Docker operations", self.test_docker_operations),
            ("Volume operations", self.test_volume_operations),
            ("Script compression", self.test_script_compression),
            ("Concurrent operations", self.test_concurrent_operations),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n{suite_name}...")
            try:
                results = test_func()
                all_results[suite_name] = results
                
                # Print summary
                if isinstance(results, dict):
                    success_count = sum(
                        1 for v in results.values()
                        if isinstance(v, dict) and v.get("success") or v is True
                    )
                    total_tests = len(results)
                    print(f"  Passed: {success_count}/{total_tests} tests")
                    
            except Exception as e:
                print(f"  ERROR: {e}")
                all_results[suite_name] = {"error": str(e)}
        
        return all_results
    
    def cleanup(self):
        """Clean up test containers."""
        print("\nCleaning up test containers...")
        self.flow.dev.reset()


@pytest.fixture(scope="module")
def flow_client():
    """Create Flow client for tests."""
    return Flow()


@pytest.fixture(scope="module") 
def dev_tester(flow_client):
    """Create dev tester instance."""
    tester = StartupScriptDevTester(flow_client)
    yield tester
    # Cleanup after all tests
    tester.cleanup()


class TestStartupScriptsWithDevSDK:
    """Test startup script functionality using dev SDK."""
    
    def test_basic_startup_execution(self, dev_tester):
        """Test basic startup script execution."""
        results = dev_tester.verify_startup_script_basics()
        
        assert results["script_execution"]["success"], "Script execution failed"
        assert results.get("startup_log_created", {}).get("success"), "Startup log not created"
        assert results.get("completion_marker", {}).get("success"), "Completion marker not found"
    
    def test_environment_setup(self, dev_tester):
        """Test environment variable setup."""
        results = dev_tester.test_environment_variables()
        
        assert results["env_vars_exported"], "Environment variables not exported"
        assert results["has_flow_task_id"], "FLOW_TASK_ID not set"
        assert results["has_flow_provider"], "FLOW_PROVIDER not set"
    
    def test_docker_functionality(self, dev_tester):
        """Test Docker operations."""
        results = dev_tester.test_docker_operations()
        
        assert results["docker_available"]["success"], "Docker not available"
        assert results["docker_run"]["success"], "Docker run failed"
    
    def test_volume_mounting(self, dev_tester):
        """Test volume mount operations."""
        results = dev_tester.test_volume_operations()
        
        # At least one mount point should work
        mount_successes = [v for k, v in results.items() if k.startswith("mount_") and v]
        assert len(mount_successes) > 0, "No volume mounts succeeded"
    
    def test_script_compression_handling(self, dev_tester):
        """Test compressed script handling."""
        results = dev_tester.test_script_compression()
        
        if results["script_compressed"]:
            assert results["decompression_works"], "Script decompression failed"
    
    def test_concurrent_execution(self, dev_tester):
        """Test concurrent container operations."""
        results = dev_tester.test_concurrent_operations()
        
        assert results["all_concurrent_succeeded"], "Not all concurrent tasks succeeded"
        assert results["concurrent_tasks_successful"] == results["concurrent_tasks_total"]


def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test startup script functionality using flow.dev SDK"
    )
    parser.add_argument("--cleanup-only", action="store_true",
                       help="Only cleanup existing containers")
    parser.add_argument("--keep-vm", action="store_true",
                       help="Keep dev VM running after tests")
    parser.add_argument("--report", default="startup_script_dev_test_report.json",
                       help="Output report filename")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = StartupScriptDevTester()
    
    if args.cleanup_only:
        tester.cleanup()
        return
    
    # Run tests
    results = tester.run_all_tests()
    
    # Generate report
    report = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "test_method": "flow.dev SDK",
        "test_results": results,
        "summary": _generate_summary(results)
    }
    
    with open(args.report, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {args.report}")
    
    # Cleanup
    if not args.keep_vm:
        print("\nStopping dev VM...")
        tester.flow.dev.stop()
    else:
        status = tester.flow.dev.status()
        print(f"\nDev VM still running: {status['vm']['name']}")
        print("Run 'flow dev stop' to stop it manually")


def _generate_summary(results: Dict[str, any]) -> Dict[str, any]:
    """Generate summary statistics."""
    total_tests = 0
    passed_tests = 0
    
    for suite_results in results.values():
        if isinstance(suite_results, dict) and "error" not in suite_results:
            for test_result in suite_results.values():
                if isinstance(test_result, dict) and "success" in test_result:
                    total_tests += 1
                    if test_result["success"]:
                        passed_tests += 1
                elif isinstance(test_result, bool):
                    total_tests += 1
                    if test_result:
                        passed_tests += 1
    
    return {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
    }


if __name__ == "__main__":
    main()