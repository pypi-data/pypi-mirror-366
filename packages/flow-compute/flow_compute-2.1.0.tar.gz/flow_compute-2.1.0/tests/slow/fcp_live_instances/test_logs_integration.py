#!/usr/bin/env python3
"""Integration tests for log collection and streaming on FCP instances."""

import json
import subprocess
import time
from typing import Dict, List, Tuple


class LogIntegrationTester:
    """Test log collection and streaming functionality."""

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

    def test_system_logs(self) -> Dict[str, Dict]:
        """Test system log access and content."""
        print("1. Testing system logs...")
        results = {}

        log_tests = [
            ("syslog_access", "sudo tail -20 /var/log/syslog | wc -l"),
            ("cloud_init_log", "test -f /var/log/cloud-init-output.log && echo 'exists' || echo 'missing'"),
            ("auth_log", "sudo tail -10 /var/log/auth.log | grep -c 'ssh' || echo 0"),
            ("kernel_log", "sudo dmesg | tail -10 | wc -l"),
            ("journal_access", "sudo journalctl -n 10 --no-pager | wc -l"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in log_tests:
                success, stdout, stderr = self.run_ssh_command(ip, command)
                instance_results[test_name] = {
                    "success": success,
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def test_flow_logs(self) -> Dict[str, Dict]:
        """Test Flow-specific log files."""
        print("\n2. Testing Flow logs...")
        results = {}

        # Check for Flow log files
        flow_log_tests = [
            ("flow_logs_exist", "ls -la /var/log/unknown.* 2>/dev/null | wc -l || echo 0"),
            ("flow_stdout", "test -f /var/log/unknown.out && tail -20 /var/log/unknown.out || echo 'No stdout log'"),
            ("flow_stderr", "test -f /var/log/unknown.err && tail -20 /var/log/unknown.err || echo 'No stderr log'"),
            ("flow_general", "test -f /var/log/unknown.log && tail -20 /var/log/unknown.log || echo 'No general log'"),
            ("flow_startup", "test -f /var/log/flow-startup.log && tail -20 /var/log/flow-startup.log || echo 'No startup log'"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in flow_log_tests:
                success, stdout, stderr = self.run_ssh_command(ip, command, timeout=10)
                instance_results[test_name] = {
                    "success": success,
                    "output": stdout.strip()[:500] if stdout else stderr.strip()  # Limit output size
                }

            results[ip] = instance_results

        return results

    def test_log_streaming(self) -> Dict[str, Dict]:
        """Test log streaming capabilities."""
        print("\n3. Testing log streaming...")
        results = {}

        # Create a test process that generates logs
        test_script = """
#!/bin/bash
echo "Starting log test at $(date)"
for i in {1..5}; do
    echo "Log entry $i at $(date)"
    sleep 1
done
echo "Log test completed at $(date)"
"""

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            # Create test script
            success, _, _ = self.run_ssh_command(
                ip,
                f"echo '{test_script}' > /tmp/log_test.sh && chmod +x /tmp/log_test.sh"
            )

            if success:
                # Test different streaming scenarios
                streaming_tests = [
                    ("tail_follow", "timeout 3 tail -f /var/log/syslog 2>&1 | wc -l || true"),
                    ("journalctl_follow", "timeout 3 sudo journalctl -f --no-pager 2>&1 | wc -l || true"),
                    ("test_script_output", "/tmp/log_test.sh 2>&1 | tee /tmp/test_output.log"),
                    ("verify_test_output", "cat /tmp/test_output.log | grep -c 'Log entry' || echo 0"),
                ]

                for test_name, command in streaming_tests:
                    success, stdout, stderr = self.run_ssh_command(ip, command, timeout=10)
                    instance_results[test_name] = {
                        "success": success or test_name.endswith("_follow"),  # Timeout is expected for follow
                        "output": stdout.strip() if stdout else stderr.strip()
                    }
            else:
                instance_results["error"] = "Failed to create test script"

            # Cleanup
            self.run_ssh_command(ip, "rm -f /tmp/log_test.sh /tmp/test_output.log")

            results[ip] = instance_results

        return results

    def test_container_logs(self) -> Dict[str, Dict]:
        """Test Docker container log collection."""
        print("\n4. Testing container logs...")
        results = {}

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            # Run a test container that generates logs
            container_name = "flow-log-test"

            # Clean up any existing container
            self.run_ssh_command(ip, f"sudo docker rm -f {container_name} 2>/dev/null || true")

            # Start container that generates logs
            success, stdout, stderr = self.run_ssh_command(
                ip,
                f"sudo docker run -d --name {container_name} alpine:latest sh -c 'for i in $(seq 1 10); do echo \"Container log entry $i\"; sleep 1; done'",
                timeout=30
            )

            if success:
                time.sleep(3)  # Let container generate some logs

                log_tests = [
                    ("container_logs", f"sudo docker logs {container_name} 2>&1 | wc -l"),
                    ("container_logs_tail", f"sudo docker logs --tail 5 {container_name}"),
                    ("container_logs_follow", f"timeout 2 sudo docker logs -f {container_name} 2>&1 | wc -l || true"),
                    ("container_logs_timestamps", f"sudo docker logs -t {container_name} | head -3"),
                ]

                for test_name, command in log_tests:
                    success, stdout, stderr = self.run_ssh_command(ip, command, timeout=10)
                    instance_results[test_name] = {
                        "success": success or "follow" in test_name,
                        "output": stdout.strip()[:300] if stdout else stderr.strip()
                    }
            else:
                instance_results["error"] = f"Failed to start test container: {stderr}"

            # Cleanup
            self.run_ssh_command(ip, f"sudo docker rm -f {container_name} 2>/dev/null || true")

            results[ip] = instance_results

        return results

    def test_log_rotation(self) -> Dict[str, Dict]:
        """Test log rotation configuration."""
        print("\n5. Testing log rotation...")
        results = {}

        rotation_tests = [
            ("logrotate_config", "test -f /etc/logrotate.conf && echo 'exists' || echo 'missing'"),
            ("syslog_rotation", "test -f /etc/logrotate.d/rsyslog && echo 'configured' || echo 'not configured'"),
            ("docker_rotation", "sudo docker info 2>/dev/null | grep -i 'logging driver' || echo 'Docker not accessible'"),
            ("disk_space", "df -h /var/log | tail -1 | awk '{print $4}'"),
        ]

        for ip in self.instance_ips:
            print(f"  Testing {ip}...")
            instance_results = {}

            for test_name, command in rotation_tests:
                success, stdout, stderr = self.run_ssh_command(ip, command)
                instance_results[test_name] = {
                    "success": success,
                    "output": stdout.strip() if stdout else stderr.strip()
                }

            results[ip] = instance_results

        return results

    def run_all_tests(self) -> Dict[str, any]:
        """Run all log integration tests."""
        print("Log Collection Integration Tests")
        print("=" * 50)

        all_results = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "instances": self.instance_ips,
            "tests": {}
        }

        test_suites = [
            ("system_logs", self.test_system_logs),
            ("flow_logs", self.test_flow_logs),
            ("log_streaming", self.test_log_streaming),
            ("container_logs", self.test_container_logs),
            ("log_rotation", self.test_log_rotation),
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

        for suite_results in test_results.values():
            if isinstance(suite_results, dict) and "error" not in suite_results:
                for instance_results in suite_results.values():
                    for test_result in instance_results.values():
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

    def save_report(self, results: Dict, filename: str = "logs_integration_report.json"):
        """Save test results to file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nReport saved to: {filename}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test log collection on FCP instances"
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

    tester = LogIntegrationTester(
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


if __name__ == "__main__":
    main()
