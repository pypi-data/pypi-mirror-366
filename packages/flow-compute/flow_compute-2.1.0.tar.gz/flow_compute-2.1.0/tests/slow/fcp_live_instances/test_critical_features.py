#!/usr/bin/env python3
"""Test critical FCP features: Docker image caching and nvidia-smi log output."""

import json
import subprocess
import time
from typing import Dict, List, Tuple


class CriticalFeaturesTester:
    """Test Docker caching and nvidia-smi logging."""

    def __init__(self, instance_ips: List[str], ssh_key_path: str):
        self.instance_ips = instance_ips
        self.ssh_key_path = ssh_key_path

    def run_ssh_command(self, ip: str, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run SSH command on instance."""
        ssh_args = [
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-i", self.ssh_key_path,
            f"ubuntu@{ip}", command
        ]

        try:
            result = subprocess.run(ssh_args, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def test_docker_image_caching(self) -> Dict[str, Dict]:
        """Test Docker image caching functionality."""
        print("\n1. Testing Docker Image Caching")
        print("=" * 50)

        results = {}
        test_images = [
            "alpine:latest",
            "nvidia/cuda:11.8.0-base-ubuntu22.04",
            "python:3.10-slim"
        ]

        for ip in self.instance_ips:
            print(f"\nTesting on {ip}:")
            instance_results = {"caching_tests": {}}

            # First, check existing images
            print("  Checking existing images...")
            success, stdout, _ = self.run_ssh_command(
                ip, "sudo docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}'"
            )
            instance_results["existing_images"] = stdout.strip() if success else "Failed to list images"

            # Test pulling and caching each image
            for image in test_images:
                print(f"  Testing {image}...")

                # Remove image if exists
                self.run_ssh_command(ip, f"sudo docker rmi {image} 2>/dev/null || true")

                # First pull - measure time
                start_time = time.time()
                success1, output1, _ = self.run_ssh_command(
                    ip, f"sudo docker pull {image}", timeout=120
                )
                first_pull_time = time.time() - start_time

                if success1:
                    # Remove and pull again to test caching
                    self.run_ssh_command(ip, f"sudo docker rmi {image}")

                    start_time = time.time()
                    success2, output2, _ = self.run_ssh_command(
                        ip, f"sudo docker pull {image}", timeout=120
                    )
                    second_pull_time = time.time() - start_time

                    # Check if image is cached (second pull should be faster)
                    cache_speedup = first_pull_time / second_pull_time if second_pull_time > 0 else 0

                    instance_results["caching_tests"][image] = {
                        "first_pull_time": f"{first_pull_time:.2f}s",
                        "second_pull_time": f"{second_pull_time:.2f}s",
                        "cache_speedup": f"{cache_speedup:.2f}x",
                        "caching_effective": cache_speedup > 1.5
                    }
                else:
                    instance_results["caching_tests"][image] = {"error": "Failed to pull image"}

            # Check Docker cache directory
            success, stdout, _ = self.run_ssh_command(
                ip, "sudo du -sh /var/lib/docker/overlay2 2>/dev/null || echo 'No overlay2 directory'"
            )
            instance_results["cache_directory_size"] = stdout.strip()

            # Check Docker system df for cache info
            success, stdout, _ = self.run_ssh_command(
                ip, "sudo docker system df"
            )
            instance_results["docker_disk_usage"] = stdout.strip() if success else "Failed"

            results[ip] = instance_results

        return results

    def test_nvidia_smi_logging(self) -> Dict[str, Dict]:
        """Test nvidia-smi execution and log output."""
        print("\n\n2. Testing nvidia-smi Logging")
        print("=" * 50)

        results = {}

        for ip in self.instance_ips:
            print(f"\nTesting on {ip}:")
            instance_results = {}

            # Run nvidia-smi and capture output
            print("  Running nvidia-smi...")
            success, stdout, stderr = self.run_ssh_command(
                ip, "nvidia-smi", timeout=10
            )

            if success:
                instance_results["nvidia_smi_output"] = stdout
                print("  ✓ nvidia-smi executed successfully")

                # Save to different log locations
                log_locations = [
                    "/tmp/nvidia-smi.log",
                    "/var/log/nvidia-smi.log",
                    "/home/ubuntu/nvidia-smi.log"
                ]

                for log_path in log_locations:
                    # Try to write log
                    cmd = f"nvidia-smi | sudo tee {log_path} > /dev/null && echo 'Success: {log_path}'"
                    success, output, _ = self.run_ssh_command(ip, cmd)

                    if success and "Success" in output:
                        # Verify we can read it back
                        success2, content, _ = self.run_ssh_command(
                            ip, f"sudo head -20 {log_path}"
                        )
                        instance_results[f"log_{log_path}"] = {
                            "write_success": True,
                            "read_success": success2,
                            "preview": content[:200] + "..." if success2 else "Failed to read"
                        }
                    else:
                        instance_results[f"log_{log_path}"] = {
                            "write_success": False,
                            "error": "Failed to write"
                        }

                # Test continuous logging
                print("  Testing continuous nvidia-smi logging...")
                script = """#!/bin/bash
                LOG_FILE=/tmp/nvidia-smi-continuous.log
                echo "Starting nvidia-smi monitoring at $(date)" > $LOG_FILE
                for i in {1..5}; do
                    echo "=== Iteration $i at $(date) ===" >> $LOG_FILE
                    nvidia-smi --query-gpu=timestamp,name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free --format=csv >> $LOG_FILE
                    sleep 2
                done
                echo "Monitoring complete at $(date)" >> $LOG_FILE
                cat $LOG_FILE
                """

                success, output, _ = self.run_ssh_command(
                    ip, f"echo '{script}' > /tmp/monitor.sh && chmod +x /tmp/monitor.sh && /tmp/monitor.sh",
                    timeout=30
                )

                instance_results["continuous_monitoring"] = {
                    "success": success,
                    "output": output if success else "Failed to run monitoring script"
                }

                # Test output to Flow logs
                print("  Testing output to Flow logs...")
                flow_log_test = """
                # Write to various Flow log locations
                nvidia-smi | sudo tee -a /var/log/unknown.out
                nvidia-smi --query-gpu=name,memory.total --format=csv | sudo tee -a /var/log/unknown.log
                echo "nvidia-smi test at $(date)" | sudo tee -a /var/log/unknown.log
                """

                success, _, _ = self.run_ssh_command(ip, flow_log_test)

                # Read back Flow logs
                success2, flow_logs, _ = self.run_ssh_command(
                    ip, "sudo tail -30 /var/log/unknown.log"
                )

                instance_results["flow_logs_integration"] = {
                    "write_success": success,
                    "read_success": success2,
                    "log_content": flow_logs[-500:] if success2 else "Failed to read"
                }

            else:
                instance_results["error"] = f"nvidia-smi failed: {stderr}"

            results[ip] = instance_results

        return results

    def run_all_tests(self) -> Dict:
        """Run all critical feature tests."""
        print("Critical Features Test Suite")
        print("=" * 50)

        all_results = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "instances": self.instance_ips,
            "tests": {}
        }

        # Test Docker caching
        caching_results = self.test_docker_image_caching()
        all_results["tests"]["docker_caching"] = caching_results

        # Test nvidia-smi logging
        nvidia_results = self.test_nvidia_smi_logging()
        all_results["tests"]["nvidia_smi_logging"] = nvidia_results

        return all_results

    def save_report(self, results: Dict):
        """Save test report."""
        with open("critical_features_report.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n\nReport saved to: critical_features_report.json")

        # Print summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)

        # Docker caching summary
        print("\nDocker Image Caching:")
        for ip, data in results["tests"]["docker_caching"].items():
            print(f"\n  Instance {ip}:")
            if "caching_tests" in data:
                for image, test in data["caching_tests"].items():
                    if "caching_effective" in test:
                        status = "✓" if test["caching_effective"] else "✗"
                        print(f"    {image}: {status} (speedup: {test['cache_speedup']})")
                    else:
                        print(f"    {image}: ✗ {test.get('error', 'Unknown error')}")

        # nvidia-smi logging summary
        print("\nnvidia-smi Logging:")
        for ip, data in results["tests"]["nvidia_smi_logging"].items():
            print(f"\n  Instance {ip}:")
            if "error" in data:
                print(f"    ✗ {data['error']}")
            else:
                if "nvidia_smi_output" in data:
                    print("    ✓ nvidia-smi execution successful")
                if "flow_logs_integration" in data:
                    status = "✓" if data["flow_logs_integration"]["write_success"] else "✗"
                    print(f"    {status} Flow logs integration")
                if "continuous_monitoring" in data:
                    status = "✓" if data["continuous_monitoring"]["success"] else "✗"
                    print(f"    {status} Continuous monitoring")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python test_critical_features.py <instance_ip1> [instance_ip2...] --key <ssh_key>")
        sys.exit(1)

    # Parse arguments
    instance_ips = []
    ssh_key = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--key" and i + 1 < len(sys.argv):
            ssh_key = sys.argv[i + 1]
            i += 2
        else:
            instance_ips.append(sys.argv[i])
            i += 1

    if not ssh_key:
        print("Error: --key argument required")
        sys.exit(1)

    # Run tests
    tester = CriticalFeaturesTester(instance_ips, ssh_key)
    results = tester.run_all_tests()
    tester.save_report(results)


if __name__ == "__main__":
    main()
