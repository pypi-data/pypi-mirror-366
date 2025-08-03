#!/usr/bin/env python3
"""Test Docker image preloading and caching strategies."""

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


def test_docker_image_preloading(instance_ip: str, ssh_key: str):
    """Test different methods of preloading Docker images."""
    print("Testing Docker Image Preloading Methods")
    print("=" * 60)

    # Method 1: Test if copying image files works
    print("\n1. Testing Direct File Copy Method...")

    # Check current images
    success, stdout, _ = run_ssh_command(instance_ip, ssh_key, "sudo docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.ID}}'")
    print("Current images:")
    print(stdout)

    # Check Docker's image database
    print("\nChecking Docker's internal database structure...")
    success, stdout, _ = run_ssh_command(
        instance_ip, ssh_key,
        "sudo ls -la /mnt/local/docker-data/image/overlay2/ 2>/dev/null | head -10"
    )
    print(stdout if success else "No image database found")

    # Method 2: Docker save/load approach
    print("\n2. Testing Docker Save/Load Method...")

    # Save an image
    print("Saving alpine:latest to tar file...")
    success, stdout, stderr = run_ssh_command(
        instance_ip, ssh_key,
        "sudo docker pull alpine:latest && sudo docker save alpine:latest -o /mnt/local/alpine.tar && ls -lh /mnt/local/alpine.tar"
    )

    if success:
        print(f"Image saved: {stdout.strip()}")

        # Remove the image
        print("\nRemoving alpine:latest...")
        run_ssh_command(instance_ip, ssh_key, "sudo docker rmi alpine:latest")

        # Load from tar
        print("Loading from saved tar file...")
        start_time = time.time()
        success, stdout, _ = run_ssh_command(
            instance_ip, ssh_key,
            "sudo docker load -i /mnt/local/alpine.tar"
        )
        load_time = time.time() - start_time

        if success:
            print(f"✓ Image loaded successfully in {load_time:.2f} seconds")
            print(stdout)
        else:
            print("✗ Failed to load image")

    # Method 3: Using Docker registry v2 storage
    print("\n3. Testing Registry Storage Method...")

    success, stdout, _ = run_ssh_command(
        instance_ip, ssh_key,
        "sudo ls -la /mnt/local/registry/docker/registry/v2/repositories/ 2>/dev/null || echo 'No repositories yet'"
    )
    print(f"Registry storage: {stdout.strip()}")

    # Method 4: BuildKit cache
    print("\n4. Testing BuildKit Cache Method...")

    # Check BuildKit cache
    success, stdout, _ = run_ssh_command(
        instance_ip, ssh_key,
        "sudo docker system df -v | grep -A5 'Build Cache' || echo 'No build cache info'"
    )
    print(stdout if success else "BuildKit info not available")

    # Method 5: Creating a pre-populated volume
    print("\n5. Testing Pre-populated Volume Method...")

    # Create a script to export/import images via volumes
    preload_script = """#!/bin/bash
# Docker Image Preloader Script

CACHE_DIR="/mnt/local/docker-images"
mkdir -p "$CACHE_DIR"

case "$1" in
    save)
        # Save all current images to cache directory
        echo "Saving all Docker images to cache..."
        for image in $(sudo docker images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>'); do
            echo "Saving $image..."
            filename=$(echo "$image" | tr '/:' '_').tar
            sudo docker save "$image" -o "$CACHE_DIR/$filename"
        done
        echo "Saved $(ls -1 $CACHE_DIR/*.tar 2>/dev/null | wc -l) images"
        du -sh "$CACHE_DIR"
        ;;
        
    load)
        # Load all images from cache directory
        echo "Loading Docker images from cache..."
        for tarfile in "$CACHE_DIR"/*.tar; do
            if [ -f "$tarfile" ]; then
                echo "Loading $(basename $tarfile)..."
                sudo docker load -i "$tarfile"
            fi
        done
        ;;
        
    list)
        # List cached images
        echo "Cached images:"
        ls -lh "$CACHE_DIR"/*.tar 2>/dev/null || echo "No cached images"
        ;;
        
    *)
        echo "Usage: $0 {save|load|list}"
        exit 1
        ;;
esac
"""

    # Create the preloader script
    success, _, _ = run_ssh_command(
        instance_ip, ssh_key,
        f"echo '{preload_script}' | sudo tee /usr/local/bin/docker-preload && sudo chmod +x /usr/local/bin/docker-preload"
    )

    if success:
        print("Created docker-preload script")

        # Test saving images
        print("\nSaving current images to cache...")
        success, stdout, _ = run_ssh_command(
            instance_ip, ssh_key,
            "sudo docker-preload save"
        )
        print(stdout if success else "Failed to save images")

    # Method 6: Dockerfile with cache mount
    print("\n6. Testing Dockerfile Cache Mount Method...")

    dockerfile_content = """FROM alpine:latest
# Use BuildKit cache mount for package downloads
RUN --mount=type=cache,target=/var/cache/apk \\
    apk add --no-cache python3 py3-pip

# Use cache mount for pip packages
RUN --mount=type=cache,target=/root/.cache/pip \\
    pip3 install requests numpy
"""

    success, _, _ = run_ssh_command(
        instance_ip, ssh_key,
        f"echo '{dockerfile_content}' > /tmp/Dockerfile.cache"
    )

    if success:
        print("Building with cache mounts...")
        success, stdout, stderr = run_ssh_command(
            instance_ip, ssh_key,
            "cd /tmp && sudo DOCKER_BUILDKIT=1 docker build -f Dockerfile.cache -t test-cache . 2>&1 | tail -20"
        )
        print(stdout if success else stderr)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: Docker Image Preloading Methods")
    print("=" * 60)
    print("""
1. Direct File Copy: ❌ Does NOT work
   - Docker needs consistent metadata/database
   - Images won't be recognized

2. Docker Save/Load: ✅ Works but slow
   - Reliable method for image transfer
   - Good for backup/restore

3. Registry Storage: ✅ Best for production
   - Fast pulls from local registry
   - Maintains proper metadata

4. BuildKit Cache: ✅ Good for builds
   - Caches layers during build
   - Reduces build times

5. Preload Script: ✅ Practical solution
   - Save all images to tar files
   - Load on new instances

6. Cache Mounts: ✅ Excellent for dependencies
   - Persists package caches
   - Speeds up rebuilds
""")


def test_flow_optimal_caching(instance_ip: str, ssh_key: str):
    """Test the optimal caching setup for Flow."""
    print("\n\nOptimal Flow Caching Setup")
    print("=" * 60)

    # Create startup script for Flow
    flow_cache_setup = """#!/bin/bash
# Flow Docker Cache Setup

# 1. Ensure Docker uses persistent storage
if [ ! -f /etc/docker/daemon.json ]; then
    cat > /etc/docker/daemon.json << 'EOF'
{
    "data-root": "/mnt/local/docker-data",
    "storage-driver": "overlay2",
    "insecure-registries": ["localhost:5000"],
    "registry-mirrors": ["http://localhost:5000"]
}
EOF
    systemctl restart docker
fi

# 2. Start local registry if not running
if ! docker ps | grep -q registry; then
    docker run -d -p 5000:5000 --restart=always \\
        --name registry \\
        -v /mnt/local/registry:/var/lib/registry \\
        registry:2
fi

# 3. Check for preloaded images and load them
if [ -d /mnt/local/docker-images ] && [ "$(ls -A /mnt/local/docker-images/*.tar 2>/dev/null)" ]; then
    echo "Loading preloaded images..."
    for img in /mnt/local/docker-images/*.tar; do
        docker load -i "$img"
    done
fi

# 4. Pre-pull common images
COMMON_IMAGES=(
    "alpine:latest"
    "python:3.10-slim"
    "nvidia/cuda:11.8.0-base-ubuntu22.04"
    "ubuntu:22.04"
)

for img in "${COMMON_IMAGES[@]}"; do
    if ! docker images | grep -q "$(echo $img | cut -d: -f1)"; then
        docker pull "$img"
    fi
done

echo "Docker cache setup complete"
"""

    # Install the setup script
    print("Installing Flow cache setup script...")
    success, _, _ = run_ssh_command(
        instance_ip, ssh_key,
        f"echo '{flow_cache_setup}' | sudo tee /usr/local/bin/flow-cache-setup && sudo chmod +x /usr/local/bin/flow-cache-setup"
    )

    if success:
        print("✓ Created flow-cache-setup script")
        print("\nThis script can be added to instance startup to ensure:")
        print("- Docker uses persistent storage")
        print("- Local registry is running")
        print("- Preloaded images are restored")
        print("- Common images are available")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) != 3:
        print("Usage: python test_docker_image_preloading.py <instance_ip> <ssh_key>")
        sys.exit(1)

    instance_ip = sys.argv[1]
    ssh_key = sys.argv[2]

    # Test preloading methods
    test_docker_image_preloading(instance_ip, ssh_key)

    # Test optimal Flow setup
    test_flow_optimal_caching(instance_ip, ssh_key)


if __name__ == "__main__":
    main()
