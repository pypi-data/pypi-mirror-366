#!/usr/bin/env python3
"""Setup and test Docker persistent caching using external volume."""

import json
import subprocess
import time
from typing import Tuple


def run_ssh_command(ip: str, ssh_key: str, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
    """Run SSH command on instance."""
    ssh_args = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-i", ssh_key,
        f"ubuntu@{ip}", command
    ]

    try:
        result = subprocess.run(ssh_args, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def setup_persistent_docker_cache(instance_ip: str, ssh_key: str):
    """Set up Docker to use persistent storage on /mnt/local."""
    print(f"Setting up persistent Docker cache on {instance_ip}")
    print("=" * 60)

    # 1. Check current Docker status
    print("\n1. Checking current Docker configuration...")
    success, stdout, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker info | grep -E 'Root Dir:|Images:|Storage Driver:'")
    print(f"Current config:\n{stdout}")

    # 2. Create Docker data directory on persistent volume
    print("\n2. Creating Docker directory on persistent volume...")
    docker_persistent_dir = "/mnt/local/docker-data"

    commands = [
        f"sudo mkdir -p {docker_persistent_dir}",
        f"sudo chmod 755 {docker_persistent_dir}",
        "ls -la /mnt/local/"
    ]

    for cmd in commands:
        success, stdout, stderr = run_ssh_command(instance_ip, ssh_key, cmd)
        if not success:
            print(f"Error: {stderr}")
            return False

    # 3. Stop Docker service
    print("\n3. Stopping Docker service...")
    success, _, _ = run_ssh_command(instance_ip, ssh_key, "sudo systemctl stop docker")
    if not success:
        print("Failed to stop Docker")
        return False

    # 4. Copy existing Docker data (if any)
    print("\n4. Copying existing Docker data to persistent volume...")
    success, stdout, stderr = run_ssh_command(
        instance_ip, ssh_key,
        f"sudo rsync -av /var/lib/docker/ {docker_persistent_dir}/ || sudo cp -a /var/lib/docker/* {docker_persistent_dir}/ 2>/dev/null || echo 'No existing data to copy'",
        timeout=120
    )
    print("Copy completed" if success else f"Copy may have failed: {stderr}")

    # 5. Configure Docker to use new location
    print("\n5. Configuring Docker daemon...")
    daemon_config = {
        "data-root": docker_persistent_dir,
        "storage-driver": "overlay2",
        "storage-opts": [
            "overlay2.override_kernel_check=true"
        ],
        "registry-mirrors": ["https://mirror.gcr.io"],
        "log-driver": "json-file",
        "log-opts": {
            "max-size": "100m",
            "max-file": "3"
        }
    }

    config_json = json.dumps(daemon_config, indent=2)
    success, _, stderr = run_ssh_command(
        instance_ip, ssh_key,
        f"echo '{config_json}' | sudo tee /etc/docker/daemon.json"
    )

    if not success:
        print(f"Failed to write daemon.json: {stderr}")
        return False

    # 6. Start Docker with new configuration
    print("\n6. Starting Docker with new configuration...")
    success, _, stderr = run_ssh_command(instance_ip, ssh_key, "sudo systemctl start docker")
    if not success:
        print(f"Failed to start Docker: {stderr}")
        # Try to get more info
        run_ssh_command(instance_ip, ssh_key, "sudo journalctl -u docker -n 50")
        return False

    # 7. Verify new configuration
    print("\n7. Verifying new configuration...")
    time.sleep(3)  # Give Docker time to fully start

    success, stdout, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker info | grep -E 'Root Dir:|Storage Driver:'")
    print(f"New config:\n{stdout}")

    # 8. Test image persistence
    print("\n8. Testing image persistence...")

    # Pull test images
    test_images = ["alpine:latest", "nginx:alpine", "python:3.10-alpine"]

    print("Pulling test images...")
    for image in test_images:
        print(f"  Pulling {image}...")
        success, _, _ = run_ssh_command(instance_ip, ssh_key, f"sudo docker pull {image}", timeout=60)
        if not success:
            print(f"    Failed to pull {image}")

    # Check disk usage
    success, stdout, _ = run_ssh_command(instance_ip, ssh_key, f"du -sh {docker_persistent_dir}")
    print(f"\nDocker data size: {stdout.strip()}")

    # List images
    success, stdout, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker images")
    print(f"\nCached images:\n{stdout}")

    # 9. Test cache effectiveness
    print("\n9. Testing cache effectiveness...")

    # Remove and re-pull to test cache
    print("Removing alpine:latest to test re-pull speed...")
    run_ssh_command(instance_ip, ssh_key, "sudo docker rmi alpine:latest")

    start_time = time.time()
    success, stdout, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker pull alpine:latest", timeout=30)
    pull_time = time.time() - start_time

    print(f"Re-pull time: {pull_time:.2f} seconds")
    print("Note: With registry mirror, subsequent pulls should be faster")

    # 10. Create convenience script
    print("\n10. Creating convenience script...")
    script_content = f"""#!/bin/bash
# Docker cache management script

case "$1" in
    status)
        echo "Docker Persistent Cache Status:"
        echo "=============================="
        df -h {docker_persistent_dir}
        echo
        echo "Cache contents:"
        sudo du -sh {docker_persistent_dir}/*
        echo
        echo "Cached images:"
        sudo docker images
        ;;
    clean)
        echo "Cleaning Docker cache..."
        sudo docker system prune -af
        ;;
    size)
        echo "Cache size: $(sudo du -sh {docker_persistent_dir} | cut -f1)"
        ;;
    *)
        echo "Usage: $0 {{status|clean|size}}"
        exit 1
        ;;
esac
"""

    success, _, _ = run_ssh_command(
        instance_ip, ssh_key,
        f"echo '{script_content}' | sudo tee /usr/local/bin/docker-cache && sudo chmod +x /usr/local/bin/docker-cache"
    )

    if success:
        print("Created /usr/local/bin/docker-cache management script")

    print("\n" + "=" * 60)
    print("SUCCESS! Docker is now using persistent storage")
    print(f"Data directory: {docker_persistent_dir}")
    print("Management commands:")
    print("  docker-cache status  - Check cache status")
    print("  docker-cache size    - Show cache size")
    print("  docker-cache clean   - Clean cache")

    return True


def test_persistence_across_restart(instance_ip: str, ssh_key: str):
    """Test if Docker cache persists across Docker restart."""
    print("\n\nTesting persistence across Docker restart...")
    print("=" * 60)

    # List images before restart
    success, before_images, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker images --format '{{.Repository}}:{{.Tag}}'")

    # Restart Docker
    print("Restarting Docker...")
    run_ssh_command(instance_ip, ssh_key, "sudo systemctl restart docker")
    time.sleep(5)

    # List images after restart
    success, after_images, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker images --format '{{.Repository}}:{{.Tag}}'")

    print("Images before restart:")
    print(before_images)
    print("\nImages after restart:")
    print(after_images)

    if before_images == after_images:
        print("\n✅ SUCCESS: Images persisted across Docker restart!")
    else:
        print("\n❌ FAILED: Images did not persist")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python setup_docker_persistent_cache.py <instance_ip> <ssh_key>")
        sys.exit(1)

    instance_ip = sys.argv[1]
    ssh_key = sys.argv[2]

    # Setup persistent cache
    if setup_persistent_docker_cache(instance_ip, ssh_key):
        # Test persistence
        test_persistence_across_restart(instance_ip, ssh_key)
    else:
        print("\nSetup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
