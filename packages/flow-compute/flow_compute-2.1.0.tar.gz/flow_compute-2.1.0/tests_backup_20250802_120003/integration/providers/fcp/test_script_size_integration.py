"""Integration tests for script size handling in FCP provider."""

import os
from unittest.mock import Mock, patch

import pytest

from flow._internal.config import Config
from flow.api.models import TaskConfig
from flow.providers.fcp.provider import FCPProvider
from flow.providers.fcp.runtime.script_size import ScriptTooLargeError
from flow.errors import ValidationError


class TestScriptSizeIntegration:
    """Test script size handling in the full FCP provider flow."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        client = Mock()
        # Mock successful bid creation
        client.request.return_value = {"fid": "bid_123", "status": "pending"}
        return client
    
    @pytest.fixture
    def fcp_config(self):
        """Create test FCP configuration."""
        # Use a random port to avoid conflicts
        import random
        port = random.randint(9000, 9999)
        os.environ["FLOW_LOCAL_STORAGE_PORT"] = str(port)
        
        return Config(
            provider="fcp",
            auth_token="test-token",
            provider_config={
                "api_url": "https://api.test.com",
                "storage_backend": "local",
            }
        )
    
    @pytest.fixture
    def fcp_provider(self, fcp_config, mock_http_client):
        """Create FCP provider with mocked dependencies."""
        with patch('flow.providers.fcp.provider.HttpClientPool.get_client', return_value=mock_http_client):
            provider = FCPProvider(fcp_config, mock_http_client)
            # Mock project ID resolution
            provider._project_id = "test-project"
            return provider
    
    def test_small_script_passes_through(self, fcp_provider, mock_http_client):
        """Test that small scripts pass through unchanged."""
        config = TaskConfig(
            name="test-task",
            instance_type="h100",
            command="echo 'Hello World'",
            upload_code=False,
        )
        
        # Mock auction selection
        with patch.object(fcp_provider, '_check_availability') as mock_check:
            with patch.object(fcp_provider, '_select_best_region') as mock_select:
                with patch.object(fcp_provider, '_get_ssh_keys') as mock_ssh:
                    mock_check.return_value = {"us-east-1": Mock(fid="auction_123")}
                    mock_select.return_value = "us-east-1"
                    mock_ssh.return_value = []
                    
                    # This should succeed without compression
                    task = fcp_provider.submit_task("h100", config)
                    
                    # Verify the script was sent inline
                    call_args = mock_http_client.request.call_args
                    bid_spec = call_args[1]["json"]
                    startup_script = bid_spec["launch_specification"]["startup_script"]
                    # Commands are now wrapped in Docker, so check for the docker run command
                    assert "docker run" in startup_script
                    assert "'echo '\"'\"'Hello World'\"'\"''" in startup_script or "echo 'Hello World'" in startup_script
                    assert "base64 -d | gunzip" not in startup_script
    
    def test_large_script_gets_compressed(self, fcp_provider, mock_http_client):
        """Test that large scripts get compressed automatically."""
        # Create a large but compressible command
        large_command = "echo 'test line'\n" * 1000
        config = TaskConfig(
            name="test-task",
            instance_type="h100", 
            command=large_command,
            upload_code=False,
        )
        
        # Mock auction selection
        with patch.object(fcp_provider, '_check_availability') as mock_check:
            with patch.object(fcp_provider, '_select_best_region') as mock_select:
                with patch.object(fcp_provider, '_get_ssh_keys') as mock_ssh:
                    mock_check.return_value = {"us-east-1": Mock(fid="auction_123")}
                    mock_select.return_value = "us-east-1"
                    mock_ssh.return_value = []
                    
                    # This should succeed with compression
                    task = fcp_provider.submit_task("h100", config)
                    
                    # Verify the script was compressed
                    call_args = mock_http_client.request.call_args
                    bid_spec = call_args[1]["json"]
                    startup_script = bid_spec["launch_specification"]["startup_script"]
                    assert "base64 -d | gunzip" in startup_script
                    # The compression format has changed - no longer uses COMPRESSED_EOF
                    assert "Decompressing and executing startup script" in startup_script
    
    def test_incompressible_large_script_fails(self, fcp_provider):
        """Test that incompressible large scripts fail with helpful error."""
        # Create random data that won't compress well
        # Need to make it larger since Docker wrapping adds overhead
        import random
        import string
        # Create a very large random string that won't compress much
        # Using base64-like data which compresses poorly
        random_data = ''.join(random.choices(string.ascii_letters + string.digits + '+/', k=100_000))
        
        config = TaskConfig(
            name="test-task",
            instance_type="h100",
            command=f"#!/bin/bash\n# Random data: {random_data}",
            upload_code=False,
        )
        
        # Mock auction selection
        with patch.object(fcp_provider, '_check_availability') as mock_check:
            with patch.object(fcp_provider, '_select_best_region') as mock_select:
                with patch.object(fcp_provider, '_get_ssh_keys') as mock_ssh:
                    mock_check.return_value = {"us-east-1": Mock(fid="auction_123")}
                    mock_select.return_value = "us-east-1" 
                    mock_ssh.return_value = []
                    
                    # Disable storage backend to force failure
                    fcp_provider.script_size_handler.storage_backend = None
                    
                    # Also disable compression strategy to ensure it fails
                    from flow.providers.fcp.runtime.script_size.strategies import InlineStrategy
                    fcp_provider.script_size_handler.strategies = [InlineStrategy()]
                    
                    # This should fail with ValidationError
                    with pytest.raises(ValidationError) as exc_info:
                        fcp_provider.submit_task("h100", config)
                    
                    assert "Startup script too large" in str(exc_info.value)
                    assert "Disable code upload" in str(exc_info.value.suggestions)
    
    def test_upload_code_with_large_project(self, fcp_provider):
        """Test handling of large code uploads."""
        config = TaskConfig(
            name="test-task",
            instance_type="h100",
            command="python train.py",
            upload_code=True,
        )
        
        # Create incompressible large code archive
        import random
        import string
        import base64
        # Create very large random data that won't compress well
        # Need much larger size to exceed limits after all processing
        random_data = ''.join(random.choices(string.ascii_letters + string.digits + '+/', k=10_000_000))
        large_archive = base64.b64encode(random_data.encode()).decode()
        
        with patch.object(fcp_provider, '_package_local_code') as mock_package:
            with patch.object(fcp_provider, '_check_availability') as mock_check:
                with patch.object(fcp_provider, '_select_best_region') as mock_select:
                    with patch.object(fcp_provider, '_get_ssh_keys') as mock_ssh:
                        # Mock the code packaging to add large archive
                        def add_large_archive(cfg):
                            env = cfg.env.copy() if cfg.env else {}
                            env["_FLOW_CODE_ARCHIVE"] = large_archive
                            return cfg.model_copy(update={"env": env})
                        
                        mock_package.side_effect = add_large_archive
                        mock_check.return_value = {"us-east-1": Mock(fid="auction_123")}
                        mock_select.return_value = "us-east-1"
                        mock_ssh.return_value = []
                        
                        # Disable storage backend to force failure
                        fcp_provider.script_size_handler.storage_backend = None
                        
                        # Also disable compression strategy to ensure it fails
                        from flow.providers.fcp.runtime.script_size.strategies import InlineStrategy
                        fcp_provider.script_size_handler.strategies = [InlineStrategy()]
                        
                        # This should fail with helpful error
                        with pytest.raises(ValidationError) as exc_info:
                            fcp_provider.submit_task("h100", config)
                        
                        assert "Startup script too large" in str(exc_info.value)
                        assert "upload_code=False" in str(exc_info.value.suggestions)