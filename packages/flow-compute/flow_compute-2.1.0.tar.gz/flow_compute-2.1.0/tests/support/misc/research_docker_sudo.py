#!/usr/bin/env python3
"""Quick Docker test with sudo permissions."""

import subprocess
import sys


def test_docker_with_sudo(instance_ip, ssh_key):
    """Test Docker functionality using sudo."""

    tests = [
        ("Docker version", "sudo docker version --format 'Server: {{.Server.Version}}'"),
        ("Docker info", "sudo docker info --format 'Containers: {{.Containers}}, Images: {{.Images}}'"),
        ("GPU access", "sudo docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi -L | head -5"),
        ("Container test", "sudo docker run --rm alpine:latest echo 'Docker works!'"),
        ("User groups", "groups"),
        ("Docker socket permissions", "ls -la /var/run/docker.sock"),
    ]

    ssh_base = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-i", ssh_key,
        f"ubuntu@{instance_ip}"
    ]

    print(f"\nTesting Docker on {instance_ip} with sudo...")
    print("=" * 50)

    for test_name, command in tests:
        print(f"\n{test_name}:")
        try:
            result = subprocess.run(
                ssh_base + [command],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✓ Success: {result.stdout.strip()}")
            else:
                print(f"✗ Failed: {result.stderr.strip()}")

        except Exception as e:
            print(f"✗ Error: {e}")

    # Try to add user to docker group
    print("\nAttempting to add ubuntu user to docker group...")
    fix_command = "sudo usermod -aG docker ubuntu && echo 'User added to docker group. Logout/login required.'"
    try:
        result = subprocess.run(
            ssh_base + [fix_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout.strip() if result.returncode == 0 else result.stderr.strip())
    except Exception as e:
        print(f"Failed to add user to docker group: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_docker_sudo.py <instance_ip> <ssh_key_path>")
        sys.exit(1)

    instance_ip = sys.argv[1]
    ssh_key = sys.argv[2]

    test_docker_with_sudo(instance_ip, ssh_key)
