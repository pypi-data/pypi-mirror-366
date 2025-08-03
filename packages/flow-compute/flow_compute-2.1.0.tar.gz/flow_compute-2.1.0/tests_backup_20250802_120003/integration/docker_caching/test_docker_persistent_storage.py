#!/usr/bin/env python3
"""Test Docker persistent storage using external volumes."""

import json
import subprocess
import time
from typing import Dict, List, Tuple


class DockerPersistentStorageTester:
    """Test Docker storage persistence with external volumes."""

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

    def test_storage_configuration(self) -> Dict[str, Dict]:
        """Test current storage configuration and mount points."""
        print("\n1. Checking Storage Configuration")
        print("=" * 50)

        results = {}

        for ip in self.instance_ips:
            print(f"\nTesting {ip}:")
            instance_results = {}

            # Check mount points
            print("  Checking mount points...")
            success, stdout, _ = self.run_ssh_command(ip, "df -h | grep -E '(/mnt|/data|/var/lib/docker|/docker)'")
            instance_results["mount_points"] = stdout.strip() if success else "No special mounts found"

            # Check all block devices
            success, stdout, _ = self.run_ssh_command(ip, "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT")
            instance_results["block_devices"] = stdout.strip() if success else "Failed to list devices"

            # Check Docker root directory
            success, stdout, _ = self.run_ssh_command(ip, "sudo docker info 2>/dev/null | grep -E 'Docker Root Dir:|Storage Driver:'")
            instance_results["docker_root"] = stdout.strip() if success else "Failed to get Docker info"

            # Check available volumes
            success, stdout, _ = self.run_ssh_command(ip, "ls -la /mnt/ /data/ 2>/dev/null || echo 'Standard directories only'")
            instance_results["volume_directories"] = stdout.strip()

            # Check fstab for persistent mounts
            success, stdout, _ = self.run_ssh_command(ip, "cat /etc/fstab | grep -v '^#'")
            instance_results["fstab"] = stdout.strip() if success else "Failed to read fstab"

            results[ip] = instance_results

        return results

    def test_docker_data_persistence(self) -> Dict[str, Dict]:
        """Test if Docker data directory can be moved to persistent storage."""
        print("\n\n2. Testing Docker Data Directory Persistence")
        print("=" * 50)

        results = {}

        for ip in self.instance_ips:
            print(f"\nTesting {ip}:")
            instance_results = {}

            # Check if we can create a persistent directory
            test_dirs = ["/mnt/docker-data", "/data/docker", "/var/lib/docker-persistent"]

            for test_dir in test_dirs:
                print(f"  Testing {test_dir}...")

                # Try to create directory
                success, stdout, stderr = self.run_ssh_command(
                    ip,
                    f"sudo mkdir -p {test_dir} && echo 'Created successfully' || echo 'Failed to create'"
                )

                if success and "Created successfully" in stdout:
                    # Test write permissions
                    success2, _, _ = self.run_ssh_command(
                        ip,
                        f"sudo touch {test_dir}/test-file && sudo rm {test_dir}/test-file && echo 'Write test passed'"
                    )

                    instance_results[test_dir] = {
                        "can_create": True,
                        "writable": success2,
                        "suitable_for_docker": success2
                    }
                else:
                    instance_results[test_dir] = {
                        "can_create": False,
                        "error": stderr.strip()
                    }

            # Check Docker daemon configuration options
            print("  Checking Docker daemon configuration...")
            success, stdout, _ = self.run_ssh_command(
                ip,
                "sudo systemctl cat docker.service | grep -E 'ExecStart|--data-root'"
            )
            instance_results["docker_service_config"] = stdout.strip() if success else "No custom config"

            results[ip] = instance_results

        return results

    def test_volume_backed_docker(self) -> Dict[str, Dict]:
        """Test creating Docker volumes backed by external storage."""
        print("\n\n3. Testing Volume-Backed Docker Storage")
        print("=" * 50)

        results = {}

        for ip in self.instance_ips:
            print(f"\nTesting {ip}:")
            instance_results = {}

            # Create a test volume with specific driver options
            volume_name = "flow-persistent-cache"

            # Try different volume creation strategies
            strategies = [
                {
                    "name": "local_volume",
                    "command": f"sudo docker volume create {volume_name}"
                },
                {
                    "name": "bind_mount_volume",
                    "command": f"sudo docker volume create --driver local --opt type=none --opt o=bind --opt device=/mnt/docker-cache {volume_name}-bind"
                },
                {
                    "name": "tmpfs_volume",
                    "command": f"sudo docker volume create --driver local --opt type=tmpfs --opt device=tmpfs --opt o=size=1g {volume_name}-tmpfs"
                }
            ]

            for strategy in strategies:
                print(f"  Testing {strategy['name']}...")

                # Clean up any existing volume
                self.run_ssh_command(ip, f"sudo docker volume rm {volume_name}* 2>/dev/null || true")

                # Create volume
                success, stdout, stderr = self.run_ssh_command(ip, strategy['command'])

                if success:
                    # Inspect volume
                    success2, inspect_out, _ = self.run_ssh_command(
                        ip,
                        f"sudo docker volume inspect {volume_name}* --format '{{{{json .}}}}'"
                    )

                    # Test using volume
                    test_container = "test-cache-persistence"
                    success3, _, _ = self.run_ssh_command(
                        ip,
                        f"sudo docker run --rm -v {volume_name}:/cache alpine:latest sh -c 'echo test > /cache/test.txt && cat /cache/test.txt'"
                    )

                    instance_results[strategy['name']] = {
                        "created": True,
                        "inspect": inspect_out.strip() if success2 else "Failed to inspect",
                        "usable": success3
                    }
                else:
                    instance_results[strategy['name']] = {
                        "created": False,
                        "error": stderr.strip()
                    }

            # Test Docker plugin volumes
            print("  Checking for volume plugins...")
            success, stdout, _ = self.run_ssh_command(ip, "sudo docker plugin ls")
            instance_results["volume_plugins"] = stdout.strip() if success else "No plugins found"

            results[ip] = instance_results

        return results

    def test_image_layer_caching(self) -> Dict[str, Dict]:
        """Test approaches for persistent image layer caching."""
        print("\n\n4. Testing Image Layer Caching Approaches")
        print("=" * 50)

        results = {}

        for ip in self.instance_ips:
            print(f"\nTesting {ip}:")
            instance_results = {}

            # Check current overlay2 storage
            print("  Analyzing current Docker storage...")
            success, stdout, _ = self.run_ssh_command(
                ip,
                "sudo du -sh /var/lib/docker/overlay2 2>/dev/null && sudo ls -la /var/lib/docker/ | grep -E 'overlay2|image'"
            )
            instance_results["current_storage"] = stdout.strip() if success else "Failed to analyze"

            # Test BuildKit cache mount
            print("  Testing BuildKit cache mount...")
            buildkit_test = """
cat > /tmp/Dockerfile.test << 'EOF'
FROM alpine:latest
RUN --mount=type=cache,target=/cache \
    echo "Testing cache mount" > /cache/test.txt && \
    cat /cache/test.txt
EOF

sudo DOCKER_BUILDKIT=1 docker build -t test-buildkit -f /tmp/Dockerfile.test /tmp/
"""
            success, stdout, stderr = self.run_ssh_command(ip, buildkit_test, timeout=60)
            instance_results["buildkit_cache"] = {
                "supported": success,
                "output": stdout[-500:] if success else stderr[-500:]
            }

            # Test registry mirror configuration
            print("  Testing registry mirror setup...")
            mirror_config = """
echo '{
  "registry-mirrors": ["https://mirror.gcr.io"],
  "insecure-registries": ["localhost:5000"],
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}' | sudo tee /tmp/daemon.json.test > /dev/null
cat /tmp/daemon.json.test
"""
            success, stdout, _ = self.run_ssh_command(ip, mirror_config)
            instance_results["registry_mirror_config"] = stdout.strip() if success else "Failed"

            # Check for local registry
            print("  Checking for local registry...")
            success, stdout, _ = self.run_ssh_command(
                ip,
                "sudo docker ps -a | grep registry || echo 'No local registry'"
            )
            instance_results["local_registry"] = stdout.strip()

            results[ip] = instance_results

        return results

    def run_all_tests(self) -> Dict:
        """Run all storage persistence tests."""
        print("Docker Persistent Storage Test Suite")
        print("=" * 50)

        all_results = {
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "instances": self.instance_ips,
            "tests": {}
        }

        # Run test suites
        test_suites = [
            ("storage_configuration", self.test_storage_configuration),
            ("docker_data_persistence", self.test_docker_data_persistence),
            ("volume_backed_storage", self.test_volume_backed_docker),
            ("image_layer_caching", self.test_image_layer_caching),
        ]

        for suite_name, test_func in test_suites:
            try:
                results = test_func()
                all_results["tests"][suite_name] = results
            except Exception as e:
                print(f"  ERROR in {suite_name}: {e}")
                all_results["tests"][suite_name] = {"error": str(e)}

        return all_results

    def save_report(self, results: Dict):
        """Save test report and print recommendations."""
        with open("docker_persistent_storage_report.json", "w") as f:
            json.dump(results, f, indent=2)

        print("\n\nReport saved to: docker_persistent_storage_report.json")

        # Print recommendations
        print("\n" + "=" * 50)
        print("RECOMMENDATIONS FOR PERSISTENT DOCKER CACHING")
        print("=" * 50)

        print("\n1. Move Docker data directory to persistent volume:")
        print("   sudo systemctl stop docker")
        print("   sudo mv /var/lib/docker /mnt/docker-data")
        print("   sudo ln -s /mnt/docker-data /var/lib/docker")
        print("   sudo systemctl start docker")

        print("\n2. Configure Docker daemon with custom data-root:")
        print("   Edit /etc/docker/daemon.json:")
        print('   {"data-root": "/mnt/docker-data"}')

        print("\n3. Use BuildKit cache mounts for build caching:")
        print("   RUN --mount=type=cache,target=/cache ...")

        print("\n4. Set up local registry as pull-through cache:")
        print("   docker run -d -p 5000:5000 --restart=always \\")
        print("     -v /mnt/registry:/var/lib/registry \\")
        print("     --name registry registry:2")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python test_docker_persistent_storage.py <instance_ip1> [instance_ip2...] --key <ssh_key>")
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
    tester = DockerPersistentStorageTester(instance_ips, ssh_key)
    results = tester.run_all_tests()
    tester.save_report(results)


if __name__ == "__main__":
    main()
