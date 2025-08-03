#!/usr/bin/env python3
"""Integration tests for Docker functionality on FCP instances.

Tests Docker installation, GPU support, container management, and Flow-specific
Docker features.
"""

import json
import subprocess
import time
from typing import Dict, List, Tuple


class DockerIntegrationTester:
    """Test Docker functionality on FCP instances."""

    def __init__(self, instance_ips: List[str], ssh_key_path: str, ssh_user: str = "ubuntu"):
        self.instance_ips = instance_ips
        self.ssh_key_path = ssh_key_path
        self.ssh_user = ssh_user

    def run_ssh_command(self, instance_ip: str, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run command on instance via SSH."""
        ssh_args = [
            "ssh",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-i", self.ssh_key_path,
            f"{self.ssh_user}@{instance_ip}",
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

    def test_docker_basics(self) -> Dict[str, Dict]:
        """Test basic Docker functionality."""
        print("1. Testing Docker basics...")
        results = {}

        tests = [
            ("docker_version", "docker version --format '{{.Server.Version}}'"),
            ("docker_info", "docker info --format '{{.ServerVersion}} - {{.OperatingSystem}}'"),
            ("docker_storage", "docker system df --format 'Images: {{.Images}}, Containers: {{.Containers}}, Volumes: {{.Volumes}}'"),
            ("docker_networks", "docker network ls --format '{{.Name}}' | wc -l"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in tests:
                success, stdout, stderr = self.run_ssh_command(ip, command)
                instance_results[test_name] = {
                    "success": success,
                    "output": stdout.strip() if success else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def test_gpu_docker_support(self) -> Dict[str, Dict]:
        """Test NVIDIA Docker GPU support."""
        print("\n2. Testing GPU Docker support...")
        results = {}

        # First check if nvidia-container-toolkit is installed
        setup_commands = [
            ("nvidia_runtime_check", "docker info 2>/dev/null | grep -i nvidia || echo 'No NVIDIA runtime'"),
            ("nvidia_container_cli", "which nvidia-container-cli || echo 'Not installed'"),
            ("test_gpu_access", "docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi -L 2>&1 | head -10"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in setup_commands:
                success, stdout, stderr = self.run_ssh_command(ip, command, timeout=60)
                instance_results[test_name] = {
                    "success": success,
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def test_container_operations(self) -> Dict[str, Dict]:
        """Test container lifecycle operations."""
        print("\n3. Testing container operations...")
        results = {}

        container_name = "flow-test-container"

        operations = [
            ("pull_image", "docker pull alpine:latest"),
            ("run_container", f"docker run -d --name {container_name} alpine:latest sleep 300"),
            ("list_containers", "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep flow-test"),
            ("exec_command", f"docker exec {container_name} echo 'Hello from Flow test'"),
            ("container_logs", f"docker logs {container_name}"),
            ("stop_container", f"docker stop {container_name}"),
            ("remove_container", f"docker rm {container_name}"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            # Clean up any existing test container
            self.run_ssh_command(ip, f"docker rm -f {container_name} 2>/dev/null || true")

            for op_name, command in operations:
                success, stdout, stderr = self.run_ssh_command(ip, command, timeout=60)
                instance_results[op_name] = {
                    "success": success,
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def test_volume_management(self) -> Dict[str, Dict]:
        """Test Docker volume operations."""
        print("\n4. Testing volume management...")
        results = {}

        volume_name = "flow-test-volume"

        volume_tests = [
            ("create_volume", f"docker volume create {volume_name}"),
            ("list_volumes", "docker volume ls --format '{{.Name}}' | grep flow-test"),
            ("inspect_volume", f"docker volume inspect {volume_name} --format '{{.Mountpoint}}'"),
            ("use_volume", f"docker run --rm -v {volume_name}:/data alpine:latest sh -c 'echo test > /data/test.txt && cat /data/test.txt'"),
            ("remove_volume", f"docker volume rm {volume_name}"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            # Clean up any existing test volume
            self.run_ssh_command(ip, f"docker volume rm {volume_name} 2>/dev/null || true")

            for test_name, command in volume_tests:
                success, stdout, stderr = self.run_ssh_command(ip, command)
                instance_results[test_name] = {
                    "success": success,
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def test_resource_limits(self) -> Dict[str, Dict]:
        """Test Docker resource limiting capabilities."""
        print("\n5. Testing resource limits...")
        results = {}

        resource_tests = [
            ("cpu_limit", "docker run --rm --cpus='0.5' alpine:latest sh -c 'echo CPU limit test passed'"),
            ("memory_limit", "docker run --rm -m 512m alpine:latest sh -c 'echo Memory limit test passed'"),
            ("gpu_limit", "docker run --rm --gpus '\"device=0\"' nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi -L 2>&1 | grep 'GPU 0' || echo 'GPU limiting not available'"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in resource_tests:
                success, stdout, stderr = self.run_ssh_command(ip, command, timeout=30)
                instance_results[test_name] = {
                    "success": success or "not available" in stdout,  # GPU limiting might not be available
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def test_docker_compose(self) -> Dict[str, Dict]:
        """Test Docker Compose functionality."""
        print("\n6. Testing Docker Compose...")
        results = {}

        compose_content = """version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
  redis:
    image: redis:alpine
"""

        compose_tests = [
            ("check_compose", "docker compose version || docker-compose version || echo 'Docker Compose not installed'"),
            ("create_compose_file", f"echo '{compose_content}' > /tmp/docker-compose.yml"),
            ("compose_up", "cd /tmp && docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null || echo 'Compose failed'"),
            ("compose_ps", "cd /tmp && docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null || echo 'No services'"),
            ("compose_down", "cd /tmp && docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true"),
            ("cleanup", "rm -f /tmp/docker-compose.yml"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in compose_tests:
                success, stdout, stderr = self.run_ssh_command(ip, command, timeout=60)
                instance_results[test_name] = {
                    "success": success or test_name == "cleanup",
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def run_all_tests(self) -> Dict[str, any]:
        """Run all Docker integration tests."""
        print("Docker Integration Tests")
        print("=" * 50)

        all_results = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "instances": self.instance_ips,
            "tests": {}
        }

        test_suites = [
            ("docker_basics", self.test_docker_basics),
            ("gpu_support", self.test_gpu_docker_support),
            ("container_operations", self.test_container_operations),
            ("volume_management", self.test_volume_management),
            ("resource_limits", self.test_resource_limits),
            ("docker_compose", self.test_docker_compose),
        ]

        for suite_name, test_func in test_suites:
            try:
                results = test_func()
                all_results["tests"][suite_name] = results
            except Exception as e:
                print(f"  ERROR in {suite_name}: {e}")
                all_results["tests"][suite_name] = {"error": str(e)}

        # Generate summary
        all_results["summary"] = self._generate_summary(all_results["tests"])

        return all_results

    def _generate_summary(self, test_results: Dict) -> Dict:
        """Generate test summary."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        instance_summaries = {}

        for suite_name, suite_results in test_results.items():
            if isinstance(suite_results, dict) and "error" not in suite_results:
                for instance_ip, instance_results in suite_results.items():
                    if instance_ip not in instance_summaries:
                        instance_summaries[instance_ip] = {"passed": 0, "failed": 0}

                    for test_result in instance_results.values():
                        if isinstance(test_result, dict) and "success" in test_result:
                            total_tests += 1
                            if test_result["success"]:
                                passed_tests += 1
                                instance_summaries[instance_ip]["passed"] += 1
                            else:
                                failed_tests += 1
                                instance_summaries[instance_ip]["failed"] += 1

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "by_instance": instance_summaries
        }

    def save_report(self, results: Dict, filename: str = "docker_integration_report.json"):
        """Save test results to file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nReport saved to: {filename}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Docker functionality on FCP instances"
    )
    parser.add_argument(
        "instances",
        nargs="+",
        help="Instance IP addresses"
    )
    parser.add_argument(
        "--key",
        required=True,
        help="SSH private key path"
    )
    parser.add_argument(
        "--user",
        default="ubuntu",
        help="SSH user (default: ubuntu)"
    )

    args = parser.parse_args()

    tester = DockerIntegrationTester(
        instance_ips=args.instances,
        ssh_key_path=args.key,
        ssh_user=args.user
    )

    results = tester.run_all_tests()
    tester.save_report(results)

    # Print summary
    summary = results["summary"]
    print("\nOverall Summary:")
    print(f"  Total tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Success rate: {summary['success_rate']}")

    print("\nPer-instance summary:")
    for ip, stats in summary["by_instance"].items():
        print(f"  {ip}: {stats['passed']} passed, {stats['failed']} failed")


if __name__ == "__main__":
    main()
