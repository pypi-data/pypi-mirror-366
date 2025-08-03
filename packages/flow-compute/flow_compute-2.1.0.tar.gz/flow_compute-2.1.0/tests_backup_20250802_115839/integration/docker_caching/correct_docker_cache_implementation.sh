#!/bin/bash
# Correct Docker Cache Implementation for Flow Startup Scripts

# CURRENT (INCORRECT) IMPLEMENTATION:
# docker pull {context.docker_image}
# This always pulls from the internet!

# CORRECT IMPLEMENTATION OPTIONS:

# Option 1: Check if image exists locally first
echo "=== Option 1: Check Local Images First ==="
IMAGE="python:3.10-slim"
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "Image $IMAGE already exists locally"
else
    echo "Image not found locally, pulling..."
    docker pull "$IMAGE"
fi

# Option 2: Use a local registry as cache
echo -e "\n=== Option 2: Local Registry Cache ==="
# Configure Docker to use local registry
cat > /etc/docker/daemon.json << EOF
{
    "insecure-registries": ["localhost:5000"],
    "registry-mirrors": ["http://localhost:5000"]
}
EOF
systemctl restart docker

# Start local registry if not running
docker run -d -p 5000:5000 --name registry \
    -v /mnt/local/registry:/var/lib/registry \
    registry:2

# Try to pull from local registry first
LOCAL_IMAGE="localhost:5000/${IMAGE#*/}"
if docker pull "$LOCAL_IMAGE" 2>/dev/null; then
    docker tag "$LOCAL_IMAGE" "$IMAGE"
    echo "Loaded from local cache"
else
    # Pull from internet and cache it
    docker pull "$IMAGE"
    docker tag "$IMAGE" "$LOCAL_IMAGE"
    docker push "$LOCAL_IMAGE"
    echo "Pulled from internet and cached"
fi

# Option 3: Pre-loaded image tarballs
echo -e "\n=== Option 3: Pre-loaded Tarballs ==="
CACHE_DIR="/mnt/local/docker-images"
IMAGE_TAR="$CACHE_DIR/$(echo $IMAGE | tr '/:' '_').tar"

if [ -f "$IMAGE_TAR" ]; then
    echo "Loading from cached tarball..."
    docker load -i "$IMAGE_TAR"
else
    echo "No cached tarball, pulling from internet..."
    docker pull "$IMAGE"
    # Optional: save for next time
    mkdir -p "$CACHE_DIR"
    docker save "$IMAGE" -o "$IMAGE_TAR"
fi

# Option 4: BuildKit with registry cache
echo -e "\n=== Option 4: BuildKit Registry Cache ==="
export DOCKER_BUILDKIT=1
# BuildKit can use a registry as cache
docker build \
    --cache-from type=registry,ref=localhost:5000/buildcache \
    --cache-to type=registry,ref=localhost:5000/buildcache \
    -t myapp .

# RECOMMENDED SOLUTION FOR FLOW:
echo -e "\n=== Recommended Flow Implementation ==="
cat << 'FLOW_DOCKER_CACHE' > /tmp/flow_docker_cache.sh
#!/bin/bash
# Flow Docker Cache-Aware Pull

pull_docker_image() {
    local image="$1"
    
    # 1. Check if already exists
    if docker image inspect "$image" >/dev/null 2>&1; then
        echo "Image $image already cached"
        return 0
    fi
    
    # 2. Check local registry cache
    if [ -f /etc/docker/daemon.json ] && grep -q "localhost:5000" /etc/docker/daemon.json; then
        local local_tag="localhost:5000/${image#*/}"
        if docker pull "$local_tag" 2>/dev/null; then
            docker tag "$local_tag" "$image"
            echo "Loaded $image from local registry cache"
            return 0
        fi
    fi
    
    # 3. Check for pre-loaded tarball
    local cache_dir="/mnt/local/docker-images"
    local tar_file="$cache_dir/$(echo $image | tr '/:' '_').tar"
    if [ -f "$tar_file" ]; then
        docker load -i "$tar_file"
        echo "Loaded $image from tarball cache"
        return 0
    fi
    
    # 4. Pull from internet (fallback)
    echo "Pulling $image from internet..."
    docker pull "$image"
    
    # 5. Optional: Cache for next time
    if [ -d "$cache_dir" ]; then
        docker save "$image" -o "$tar_file"
    fi
    if docker ps | grep -q registry; then
        docker tag "$image" "$local_tag"
        docker push "$local_tag" 2>/dev/null || true
    fi
}

# Usage in startup script:
pull_docker_image "{context.docker_image}"
FLOW_DOCKER_CACHE

echo -e "\nThe current implementation is WRONG because:"
echo "1. 'docker pull' ALWAYS tries to pull from the internet/registry"
echo "2. It doesn't check if the image already exists locally"
echo "3. It doesn't use any caching mechanism"
echo "4. Mounting /var/lib/docker alone doesn't create a cache"
echo ""
echo "Docker needs explicit configuration to use caches!"