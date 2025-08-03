"""Test thread safety of decorator module."""

import threading
from unittest.mock import MagicMock, patch

import flow.api.decorators


def test_concurrent_singleton_init():
    """Regression test for thread safety bug in _get_app()."""
    # Mock FlowApp to avoid authentication
    with patch('flow.api.decorators.FlowApp') as MockFlowApp:
        # Track how many times FlowApp is instantiated
        instance_count = 0
        mock_instance = MagicMock()

        def track_init(*args, **kwargs):
            nonlocal instance_count
            instance_count += 1
            return mock_instance

        MockFlowApp.side_effect = track_init

        # Force fresh state
        flow.api.decorators._app = None

        instances = []
        errors = []

        def get_instance():
            try:
                instances.append(flow.api.decorators._get_app())
            except Exception as e:
                errors.append(e)

        # Create many threads to increase chance of race condition
        threads = [threading.Thread(target=get_instance) for _ in range(20)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for all to complete
        for t in threads:
            t.join()

        # Check no errors occurred
        assert not errors, f"Errors during concurrent access: {errors}"

        # FlowApp should only be instantiated once
        assert instance_count == 1, f"FlowApp instantiated {instance_count} times!"

        # All instances should be the same object
        assert len(instances) == 20
        assert all(i is instances[0] for i in instances), "Multiple app instances returned!"

        # Clean up
        flow.api.decorators._app = None
