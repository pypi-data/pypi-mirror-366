#!/usr/bin/env python3
"""Test that Docker correctly uses /var/lib/docker when mounted as a volume."""

import subprocess
import sys


def test_docker_mount(instance_ip: str, ssh_key: str):
    """Verify Docker uses mounted /var/lib/docker correctly."""

    def ssh_cmd(cmd):
        """Execute SSH command."""
        result = subprocess.run([
            "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-i", ssh_key, f"ubuntu@{instance_ip}", cmd
        ], capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr

    print("Testing Docker with /var/lib/docker mount")
    print("=" * 50)

    # 1. Check current mount
    print("\n1. Checking mounts:")
    success, stdout, _ = ssh_cmd("df -h /var/lib/docker")
    print(stdout)

    # 2. Check Docker root directory
    print("\n2. Docker root directory:")
    success, stdout, _ = ssh_cmd("sudo docker info | grep 'Docker Root Dir'")
    print(stdout.strip())

    # 3. Pull a test image
    print("\n3. Pulling test image:")
    success, stdout, _ = ssh_cmd("sudo docker pull alpine:latest")
    print("✓ Pulled alpine:latest" if success else "✗ Failed to pull")

    # 4. Check where image is stored
    print("\n4. Image storage location:")
    success, stdout, _ = ssh_cmd("sudo find /var/lib/docker -name 'repositories.json' -exec ls -la {} \\;")
    print(stdout)

    # 5. Test persistence simulation
    print("\n5. Simulating restart (stop/start Docker):")
    ssh_cmd("sudo systemctl stop docker")
    ssh_cmd("sudo systemctl start docker")

    # 6. Check if image still exists
    print("\n6. Checking if image persists:")
    success, stdout, _ = ssh_cmd("sudo docker images | grep alpine")
    if success and "alpine" in stdout:
        print("✓ Image persists after Docker restart!")
    else:
        print("✗ Image was lost")

    # 7. Verify our caching fix works
    print("\n7. Testing our caching fix:")
    success, stdout, stderr = ssh_cmd("""
    # This should NOT pull since image exists
    sudo docker image inspect alpine:latest >/dev/null 2>&1 || sudo docker pull alpine:latest
    echo "Exit code: $?"
    """)
    print(stdout)
    if "Exit code: 0" in stdout and "Pulling from" not in stdout:
        print("✓ Caching fix works - no pull needed!")
    else:
        print("✗ Image was pulled unnecessarily")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_docker_persistent_mount.py <instance_ip> <ssh_key>")
        sys.exit(1)

    test_docker_mount(sys.argv[1], sys.argv[2])
