"""Test task submission and API contract between Flow and providers."""

from unittest.mock import Mock

import httpx
import pytest

from flow.api.models import TaskConfig


class TestTaskSubmission:
    """Test the contract between Flow and providers."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock only the HTTP boundary, not internal Flow logic."""
        client = Mock(spec=httpx.Client)
        # Set up a proper response object
        response = Mock()
        response.json.return_value = {"bid_id": "123", "task_id": "task-456"}
        response.raise_for_status = Mock()
        client.post.return_value = response
        client.get.return_value = response
        return client

    def test_startup_script_generation(self):
        """Test actual startup script generation, not mocked."""
        from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder

        # Multi-line command that includes setup
        multi_line_command = """#!/bin/bash
pip install torch
export CUDA_VISIBLE_DEVICES=0
python train.py --epochs 100
"""

        config = TaskConfig(
            command=multi_line_command,
            env={"WANDB_API_KEY": "test-key"},
            instance_type="a100"  # Required field
        )

        # Test the real builder, no mocks
        builder = StartupScriptBuilder()
        startup_script = builder.build(config)
        script = startup_script.content

        # Verify script structure
        assert "#!/bin/bash" in script

        # Verify the user command is included in the script
        assert "python train.py --epochs 100" in script

        # Verify the script sets up proper error handling
        assert "set -euxo pipefail" in script
