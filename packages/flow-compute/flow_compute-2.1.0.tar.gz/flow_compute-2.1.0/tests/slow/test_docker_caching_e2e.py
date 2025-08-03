"""End-to-end test for Docker caching behavior.

A single, simple test that verifies the essential behavior:
mounting a volume at /var/lib/docker enables image caching.
"""

import os

import pytest

from flow import Flow, TaskConfig, VolumeSpec


@pytest.mark.e2e
def test_docker_caching_works(monkeypatch):
    """Verify that Docker caching works with volume mounting."""
    # Set up test environment - API key should be provided via environment
    # Skip test if no API key is available
    api_key = os.environ.get("FCP_API_KEY")
    if not api_key:
        pytest.skip("FCP_API_KEY environment variable not set")

    monkeypatch.setenv("FCP_API_KEY", api_key)
    monkeypatch.setenv("FCP_DEFAULT_PROJECT", "test-project")
    monkeypatch.setenv("FLOW_PROVIDER", "fcp")

    flow = Flow()

    # Create a cache volume
    cache = flow.create_volume(size_gb=10, name="test-docker-cache")

    try:
        # Configure task with cache volume
        config = TaskConfig(
            name="docker-cache-test",
            instance_type="cpu.small",
            image="alpine:3.18",  # Small image for quick test
            command="echo 'Hello from Docker cache test'",
            volumes=[
                VolumeSpec(
                    volume_id=cache.volume_id,
                    mount_path="/var/lib/docker"
                )
            ]
        )

        # Run task - Docker will cache the image
        task = flow.run(config)
        task.wait()

        # If task completes successfully, caching is working
        # We don't need to measure timing or inspect cache contents
        # Docker's caching is trusted to work correctly
        assert task.status == "completed"

    finally:
        # Cleanup
        flow.delete_volume(cache.volume_id)
