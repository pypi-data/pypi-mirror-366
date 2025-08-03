#!/usr/bin/env python3
"""Integration tests specifically for startup script functionality.

This module tests that startup scripts are properly injected and executed
on FCP instances, including handling of large scripts and proper encoding.
"""

import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

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


@dataclass
class StartupScriptTest:
    """Definition of a startup script test case."""

    name: str
    description: str
    script_content: str
    expected_outputs: List[str]
    expected_files: List[str] = None
    expected_env_vars: List[str] = None
    timeout: int = 60


class StartupScriptTester:
    """Test runner for startup script functionality."""

    def __init__(self, instance_ip: str, ssh_key_path: str, ssh_user: str = "ubuntu"):
        self.instance_ip = instance_ip
        self.ssh_key_path = ssh_key_path
        self.ssh_user = ssh_user

    def run_ssh_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run command on instance via SSH.
        
        Returns:
            Tuple of (success, stdout, stderr)
        """
        ssh_args = [
            "ssh",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-i", self.ssh_key_path,
            f"{self.ssh_user}@{self.instance_ip}",
            command
        ]

        try:
            result = subprocess.run(
                ssh_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)

    def verify_startup_script_basics(self) -> Dict[str, any]:
        """Verify basic startup script execution."""
        results = {}

        # Check startup script location and permissions
        tests = [
            ("script_exists", "test -f /var/lib/cloud/instance/scripts/part-001"),
            ("script_executable", "test -x /var/lib/cloud/instance/scripts/part-001"),
            ("startup_log_exists", "test -f /var/log/flow-startup.log"),
            ("cloud_init_ran", "cloud-init status --wait --long"),
            ("startup_complete_marker", "test -f /tmp/flow-startup-complete"),
        ]

        for test_name, command in tests:
            success, stdout, stderr = self.run_ssh_command(command)
            results[test_name] = {
                "success": success,
                "output": stdout.strip() if success else stderr.strip()
            }

        return results

    def check_startup_script_content(self) -> Dict[str, any]:
        """Analyze the actual startup script content."""
        results = {}

        # Get script content
        success, content, error = self.run_ssh_command(
            "sudo cat /var/lib/cloud/instance/scripts/part-001 | head -100"
        )

        if success:
            results["script_preview"] = content[:500] + "..." if len(content) > 500 else content

            # Check for key components
            components = [
                ("has_shebang", content.startswith("#!/bin/bash")),
                ("has_error_handling", "set -euo pipefail" in content),
                ("has_logging", "exec > >(tee -a" in content),
                ("has_flow_marker", "FLOW_STARTUP" in content),
                ("has_env_setup", "export FLOW_" in content),
            ]

            for name, check in components:
                results[name] = check
        else:
            results["error"] = error

        return results

    def test_environment_variables(self) -> Dict[str, any]:
        """Test that Flow environment variables are set."""
        results = {}

        # Check for Flow-specific environment variables
        success, env_output, error = self.run_ssh_command("env | grep ^FLOW_ | sort")

        if success:
            env_vars = {}
            for line in env_output.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

            results["flow_env_vars"] = env_vars
            results["env_var_count"] = len(env_vars)
        else:
            results["error"] = error

        # Check specific expected variables
        expected_vars = ["FLOW_TASK_ID", "FLOW_INSTANCE_ID", "FLOW_PROVIDER"]
        for var in expected_vars:
            success, value, _ = self.run_ssh_command(f"echo ${var}")
            results[f"has_{var.lower()}"] = bool(value.strip())

        return results

    def test_script_size_handling(self) -> Dict[str, any]:
        """Test handling of large startup scripts."""
        results = {}

        # Check the size of the startup script
        success, size_output, error = self.run_ssh_command(
            "sudo stat -c%s /var/lib/cloud/instance/scripts/part-001"
        )

        if success:
            try:
                script_size = int(size_output.strip())
                results["script_size_bytes"] = script_size
                results["script_size_kb"] = script_size // 1024

                # Check if it's base64 encoded (for large scripts)
                success, head_output, _ = self.run_ssh_command(
                    "sudo head -20 /var/lib/cloud/instance/scripts/part-001 | grep -c base64"
                )
                results["uses_base64_encoding"] = int(head_output.strip()) > 0 if success else False

            except ValueError:
                results["error"] = "Could not parse script size"
        else:
            results["error"] = error

        return results

    def test_docker_setup(self) -> Dict[str, any]:
        """Test Docker installation and configuration."""
        results = {}

        docker_tests = [
            ("docker_installed", "which docker"),
            ("docker_running", "systemctl is-active docker"),
            ("docker_version", "docker --version"),
            ("docker_hello_world", "docker run --rm hello-world 2>&1 | grep -q 'Hello from Docker'"),
            ("nvidia_docker", "which nvidia-docker || echo 'Not installed'"),
        ]

        for test_name, command in docker_tests:
            success, stdout, stderr = self.run_ssh_command(command)
            results[test_name] = {
                "success": success,
                "output": stdout.strip() if stdout else stderr.strip()
            }

        # Check Docker daemon configuration
        success, config, _ = self.run_ssh_command("cat /etc/docker/daemon.json 2>/dev/null || echo '{}'")
        if success:
            try:
                results["docker_config"] = json.loads(config)
            except json.JSONDecodeError:
                results["docker_config"] = "Invalid JSON"

        return results

    def test_gpu_setup(self) -> Dict[str, any]:
        """Test GPU driver installation and configuration."""
        results = {}

        gpu_tests = [
            ("nvidia_smi_available", "which nvidia-smi"),
            ("gpu_detected", "nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo 'No GPU'"),
            ("cuda_version", "nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null || echo 'N/A'"),
            ("gpu_memory", "nvidia-smi --query-gpu=memory.total --format=csv,noheader 2>/dev/null || echo 'N/A'"),
        ]

        for test_name, command in gpu_tests:
            success, stdout, stderr = self.run_ssh_command(command)
            results[test_name] = {
                "success": success,
                "output": stdout.strip() if stdout else "Not available"
            }

        return results

    def test_logging_setup(self) -> Dict[str, any]:
        """Test logging configuration and output."""
        results = {}

        # Check various log files
        log_files = [
            ("/var/log/flow-startup.log", "Flow startup log"),
            ("/var/log/cloud-init-output.log", "Cloud-init output"),
            ("/var/log/syslog", "System log"),
        ]

        for log_path, description in log_files:
            # Check if file exists and get line count
            success, line_count, _ = self.run_ssh_command(f"sudo wc -l < {log_path} 2>/dev/null || echo 0")

            if success:
                count = int(line_count.strip())
                results[f"{Path(log_path).stem}_lines"] = count

                # Get last few lines
                if count > 0:
                    success, tail_output, _ = self.run_ssh_command(f"sudo tail -5 {log_path}")
                    if success:
                        results[f"{Path(log_path).stem}_tail"] = tail_output.strip()
            else:
                results[f"{Path(log_path).stem}_lines"] = 0

        return results

    def run_all_tests(self) -> Dict[str, any]:
        """Run all startup script tests."""
        print(f"Testing startup scripts on {self.instance_ip}")
        print("=" * 50)

        all_results = {}

        test_suites = [
            ("Basic startup script checks", self.verify_startup_script_basics),
            ("Script content analysis", self.check_startup_script_content),
            ("Environment variables", self.test_environment_variables),
            ("Script size handling", self.test_script_size_handling),
            ("Docker setup", self.test_docker_setup),
            ("GPU setup", self.test_gpu_setup),
            ("Logging setup", self.test_logging_setup),
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
                        if isinstance(v, dict) and v.get("success")
                    )
                    total_tests = sum(
                        1 for v in results.values()
                        if isinstance(v, dict) and "success" in v
                    )
                    if total_tests > 0:
                        print(f"  Passed: {success_count}/{total_tests} tests")

            except Exception as e:
                print(f"  ERROR: {e}")
                all_results[suite_name] = {"error": str(e)}

        return all_results

    def generate_report(self, results: Dict[str, any], output_file: str = "startup_script_test_report.json"):
        """Generate test report."""
        report = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "instance_ip": self.instance_ip,
            "test_results": results,
            "summary": self._generate_summary(results)
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {output_file}")

    def _generate_summary(self, results: Dict[str, any]) -> Dict[str, any]:
        """Generate summary statistics."""
        total_tests = 0
        passed_tests = 0

        for suite_results in results.values():
            if isinstance(suite_results, dict):
                for test_result in suite_results.values():
                    if isinstance(test_result, dict) and "success" in test_result:
                        total_tests += 1
                        if test_result["success"]:
                            passed_tests += 1

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
        }


def test_startup_script_builder():
    """Test the StartupScriptBuilder class functionality."""
    print("\nTesting StartupScriptBuilder class...")
    print("-" * 50)

    # Create custom sections for testing
    class EnvironmentSection(UserScriptSection):
        """Custom environment setup section."""
        @property
        def name(self) -> str:
            return "environment"
        
        @property
        def priority(self) -> int:
            return 10
            
        def generate(self, context: ScriptContext) -> str:
            return "export FLOW_TEST=1\nexport FLOW_ENV=testing"

    class DockerInstallSection(UserScriptSection):
        """Custom docker install section."""
        @property
        def name(self) -> str:
            return "docker_install"
        
        @property
        def priority(self) -> int:
            return 20
            
        def generate(self, context: ScriptContext) -> str:
            return "# Install Docker\napt-get update && apt-get install -y docker.io"

    # Create builder with custom sections
    sections = [
        HeaderSection(),
        EnvironmentSection(),
        DockerInstallSection(),
        CompletionSection(),
    ]
    
    builder = StartupScriptBuilder(sections=sections)

    # Create a mock TaskConfig
    from flow.api.models import TaskConfig
    config = TaskConfig(
        name="test-task",
        instance_type="a100",
        command=["echo", "hello"],
    )

    # Test building script
    script_result = builder.build(config)

    print(f"Generated script size: {script_result.size_bytes} bytes")
    print(f"Script preview:\n{script_result.content[:200]}...")
    print(f"Script is valid: {script_result.is_valid}")
    print(f"Sections included: {script_result.sections}")

    # Test size validation with large content
    class LargeSection(UserScriptSection):
        """Section with large content."""
        @property
        def name(self) -> str:
            return "large_section"
        
        @property
        def priority(self) -> int:
            return 30
            
        def generate(self, context: ScriptContext) -> str:
            return "echo 'test'\n" * 10000

    # Create builder with large section
    large_sections = sections + [LargeSection()]
    large_builder = StartupScriptBuilder(sections=large_sections)

    try:
        large_script_result = large_builder.build(config)
        print(f"Large script size: {large_script_result.size_bytes} bytes")
        print(f"Script compressed: {large_script_result.compressed}")
        print("✓ Size validation passed")
    except Exception as e:
        print(f"✗ Size validation failed: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test startup script functionality on FCP instances"
    )
    parser.add_argument("instance_ip", help="Instance IP address")
    parser.add_argument("--key", required=True, help="SSH private key path")
    parser.add_argument("--user", default="ubuntu", help="SSH user")
    parser.add_argument("--test-builder", action="store_true",
                       help="Test StartupScriptBuilder class")

    args = parser.parse_args()

    if args.test_builder:
        test_startup_script_builder()
        return

    # Run instance tests
    tester = StartupScriptTester(
        instance_ip=args.instance_ip,
        ssh_key_path=args.key,
        ssh_user=args.user
    )

    results = tester.run_all_tests()
    tester.generate_report(results)


if __name__ == "__main__":
    main()
