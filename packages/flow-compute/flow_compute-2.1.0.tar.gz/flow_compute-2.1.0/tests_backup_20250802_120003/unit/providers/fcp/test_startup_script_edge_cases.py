"""Comprehensive edge case tests for startup script builder.

This module tests edge cases and boundary conditions for the startup
script generation system to ensure robustness and proper error handling.
"""

import pytest
from unittest.mock import Mock, patch
import gzip
import base64

from flow.api.models import TaskConfig, Volume
from flow.providers.fcp.runtime.startup.builder import (
    FCPStartupScriptBuilder,
    StartupScript,
    GzipCompressor,
)
from flow.providers.fcp.runtime.startup.sections import ScriptContext
from flow.providers.fcp.runtime.startup.constants import (
    SCRIPT_COMPRESSION_THRESHOLD_BYTES,
    SCRIPT_MAX_UNCOMPRESSED_SIZE_BYTES,
    SCRIPT_ABSOLUTE_MAX_SIZE_BYTES,
    MAX_ENVIRONMENT_VARIABLES,
    MAX_ENVIRONMENT_VARIABLE_NAME_LENGTH,
    MAX_ENVIRONMENT_VARIABLE_VALUE_LENGTH,
    USER_COMMAND_MAX_LENGTH,
)


class TestScriptBuilderEdgeCases:
    """Test edge cases for script builder."""
    
    @pytest.fixture
    def builder(self):
        """Create a script builder instance."""
        return FCPStartupScriptBuilder()
    
    def test_empty_config(self, builder):
        """Test building script with minimal config."""
        config = TaskConfig(
            name="empty-task",
            instance_type="cpu.small",
            command="echo hello"
        )
        
        script = builder.build(config)
        assert script.is_valid
        assert not script.compressed
        assert "#!/bin/bash" in script.content
        assert "echo hello" in script.content
    
    def test_null_command(self, builder):
        """Test building script with null command."""
        config = TaskConfig(
            name="null-command",
            instance_type="cpu.small",
            command=""
        )
        
        script = builder.build(config)
        assert script.is_valid
        assert "#!/bin/bash" in script.content
        # Empty command should still produce valid script
    
    def test_whitespace_only_command(self, builder):
        """Test command that is only whitespace."""
        config = TaskConfig(
            name="whitespace-command",
            instance_type="cpu.small",
            command="   \n\t   "
        )
        
        script = builder.build(config)
        assert script.is_valid
        # Whitespace-only commands should be handled gracefully
    
    def test_extremely_long_command(self, builder):
        """Test command that exceeds reasonable length."""
        # Create a command longer than USER_COMMAND_MAX_LENGTH
        long_command = "echo " + "x" * (USER_COMMAND_MAX_LENGTH + 1000)
        
        config = TaskConfig(
            name="long-command",
            instance_type="cpu.small",
            command=long_command
        )
        
        script = builder.build(config)
        # Should still build but may be compressed
        assert script.is_valid
        if len(long_command.encode('utf-8')) > SCRIPT_COMPRESSION_THRESHOLD_BYTES:
            assert script.compressed
    
    def test_special_characters_in_command(self, builder):
        """Test commands with special shell characters."""
        special_commands = [
            "echo 'hello world'",
            'echo "hello $USER"',
            "echo hello && echo world",
            "echo hello | grep world",
            "echo hello > /tmp/output.txt",
            "echo hello; exit 1",
            "echo $(date)",
            "echo `hostname`",
            "echo hello\\nworld",
            "echo 'hello\\'world'",
            'echo "hello\\"world"',
        ]
        
        for cmd in special_commands:
            config = TaskConfig(
                name="special-chars",
                instance_type="cpu.small",
                command=cmd
            )
            
            script = builder.build(config)
            assert script.is_valid
            # Verify command is preserved correctly
            assert cmd in script.content or script.compressed
    
    def test_unicode_in_command(self, builder):
        """Test Unicode characters in commands."""
        unicode_commands = [
            "echo '你好世界'",  # Chinese
            "echo 'مرحبا بالعالم'",  # Arabic
            "echo '🌍🌎🌏'",  # Emojis
            "echo 'Здравствуй мир'",  # Russian
            "echo '¡Hola mundo! ñáéíóú'",  # Spanish with accents
        ]
        
        for cmd in unicode_commands:
            config = TaskConfig(
                name="unicode-cmd",
                instance_type="cpu.small",
                command=cmd
            )
            
            script = builder.build(config)
            assert script.is_valid
            # Unicode should be handled properly
    
    def test_environment_variable_limits(self, builder):
        """Test environment variable edge cases."""
        # Test maximum number of environment variables
        max_env = {f"VAR_{i}": f"value_{i}" for i in range(MAX_ENVIRONMENT_VARIABLES)}
        
        config = TaskConfig(
            name="max-env",
            instance_type="cpu.small",
            command="echo hello",
            env=max_env
        )
        
        script = builder.build(config)
        assert script.is_valid
        
        # Test exceeding maximum
        too_many_env = {f"VAR_{i}": f"value_{i}" for i in range(MAX_ENVIRONMENT_VARIABLES + 10)}
        
        config_too_many = TaskConfig(
            name="too-many-env",
            instance_type="cpu.small", 
            command="echo hello",
            env=too_many_env
        )
        
        # Should still build but may have validation warnings
        script_too_many = builder.build(config_too_many)
        # The script builder should handle this gracefully
    
    def test_environment_variable_name_length(self, builder):
        """Test environment variable name length limits."""
        # Maximum length name
        max_name = "A" * MAX_ENVIRONMENT_VARIABLE_NAME_LENGTH
        config = TaskConfig(
            name="max-env-name",
            instance_type="cpu.small",
            command="echo hello",
            env={max_name: "value"}
        )
        
        script = builder.build(config)
        assert script.is_valid
        
        # Exceeding maximum name length
        too_long_name = "A" * (MAX_ENVIRONMENT_VARIABLE_NAME_LENGTH + 10)
        config_too_long = TaskConfig(
            name="long-env-name",
            instance_type="cpu.small",
            command="echo hello",
            env={too_long_name: "value"}
        )
        
        # Should handle gracefully
        script_too_long = builder.build(config_too_long)
    
    def test_environment_variable_value_length(self, builder):
        """Test environment variable value length limits."""
        # Maximum length value
        max_value = "X" * MAX_ENVIRONMENT_VARIABLE_VALUE_LENGTH
        config = TaskConfig(
            name="max-env-value",
            instance_type="cpu.small",
            command="echo hello",
            env={"LARGE_VAR": max_value}
        )
        
        script = builder.build(config)
        # Large values should trigger compression
        if len(script.content.encode('utf-8')) > SCRIPT_COMPRESSION_THRESHOLD_BYTES:
            assert script.compressed
    
    def test_special_characters_in_env_vars(self, builder):
        """Test special characters in environment variables."""
        special_env = {
            "PATH": "/usr/bin:/bin:$HOME/bin",
            "MESSAGE": "hello 'world'",
            "QUOTED": '"double quotes"',
            "NEWLINE": "line1\\nline2",
            "TAB": "col1\\tcol2",
            "BACKSLASH": "path\\to\\file",
            "DOLLAR": "cost is $100",
            "BACKTICK": "`echo dangerous`",
            "SEMICOLON": "cmd1; cmd2",
            "PIPE": "cmd1 | cmd2",
        }
        
        config = TaskConfig(
            name="special-env",
            instance_type="cpu.small",
            command="echo hello",
            env=special_env
        )
        
        script = builder.build(config)
        assert script.is_valid
    
    def test_volume_edge_cases(self, builder):
        """Test volume mounting edge cases."""
        volumes = [
            Volume(local="/", remote="/mnt/root", read_only=True),
            Volume(local="/very/long/path/with/many/segments/that/exceeds/normal/limits/and/continues/even/further", 
                   remote="/mnt/long", read_only=False),
            Volume(local="/path with spaces", remote="/mnt/spaces", read_only=False),
            Volume(local="/path/with/unicode/文档", remote="/mnt/unicode", read_only=False),
            Volume(local="/path/with-special!@#$%^&*()", remote="/mnt/special", read_only=False),
        ]
        
        for vol in volumes:
            config = TaskConfig(
                name="volume-test",
                instance_type="cpu.small",
                command="echo hello",
                volumes=[vol]
            )
            
            script = builder.build(config)
            assert script.is_valid
    
    def test_multiple_volumes_same_target(self, builder):
        """Test multiple volumes mounting to same target."""
        volumes = [
            Volume(local="/data1", remote="/mnt/data", read_only=False),
            Volume(local="/data2", remote="/mnt/data", read_only=False),  # Same remote
        ]
        
        config = TaskConfig(
            name="duplicate-mount",
            instance_type="cpu.small",
            command="echo hello",
            volumes=volumes
        )
        
        script = builder.build(config)
        # Should handle duplicate mounts gracefully
    
    def test_docker_image_edge_cases(self, builder):
        """Test various Docker image specifications."""
        images = [
            "ubuntu",  # Simple name
            "ubuntu:22.04",  # With tag
            "nvidia/cuda:11.8.0-devel-ubuntu22.04",  # Complex tag
            "gcr.io/project/image:tag",  # Registry with path
            "localhost:5000/myimage",  # Local registry
            "user/image@sha256:abcdef123456",  # With digest
            "image:latest@sha256:123456",  # Tag and digest
            "UPPERCASE/IMAGE:TAG",  # Case sensitivity
            "image-with-dash_and_underscore",  # Special chars
        ]
        
        for image in images:
            config = TaskConfig(
                name="docker-image-test",
                instance_type="cpu.small",
                command="echo hello",
                image=image
            )
            
            script = builder.build(config)
            assert script.is_valid
            assert image in script.content or script.compressed
    
    def test_gpu_instance_detection(self, builder):
        """Test GPU detection for various instance types."""
        gpu_instances = [
            "gpu.a100",
            "gpu.v100", 
            "gpu.t4",
            "a100",
            "8xa100",
            "h100",
            "8xh100",
            "nvidia-gpu-instance",
        ]
        
        for instance in gpu_instances:
            config = TaskConfig(
                name="gpu-test",
                instance_type=instance,
                command="nvidia-smi"
            )
            
            script = builder.build(config)
            assert script.is_valid
            # GPU instances should include GPU-specific setup
            if "gpu" in instance.lower() or any(gpu in instance.lower() for gpu in ["a100", "v100", "t4", "h100"]):
                assert "--gpus all" in script.content or script.compressed
    
    def test_script_compression_boundary(self, builder):
        """Test script compression at exact threshold."""
        # Create content exactly at compression threshold
        target_size = SCRIPT_COMPRESSION_THRESHOLD_BYTES
        base_content = "echo '"
        end_content = "'"
        
        # Account for script overhead
        script_with_small_cmd = builder.build(TaskConfig(
            name="test",
            instance_type="cpu.small",
            command="echo x"
        ))
        overhead = len(script_with_small_cmd.content.encode('utf-8')) - len("echo x")
        
        # Create padding to reach exact threshold
        padding_size = max(0, target_size - overhead - len(base_content) - len(end_content))
        padding = "x" * padding_size
        
        config = TaskConfig(
            name="boundary-test",
            instance_type="cpu.small",
            command=f"{base_content}{padding}{end_content}"
        )
        
        script = builder.build(config)
        assert script.is_valid
        
        # Test just over threshold
        config_over = TaskConfig(
            name="over-boundary",
            instance_type="cpu.small",
            command=f"{base_content}{padding}xx{end_content}"  # Add 2 more bytes
        )
        
        script_over = builder.build(config_over)
        assert script_over.is_valid
        assert script_over.compressed
    
    def test_compressed_script_decompression(self, builder):
        """Test that compressed scripts can be decompressed correctly."""
        # Create large content that will be compressed
        large_content = "echo 'start'\n"
        large_content += "\n".join([f"echo 'Line {i}'" for i in range(5000)])
        
        config = TaskConfig(
            name="decompress-test",
            instance_type="cpu.small",
            command=large_content
        )
        
        script = builder.build(config)
        assert script.compressed
        
        # Extract the base64 content from the bootstrap script
        import re
        match = re.search(r'echo "([^"]+)" \| base64 -d \| gunzip', script.content)
        assert match
        
        # Verify decompression works
        encoded = match.group(1)
        compressed = base64.b64decode(encoded)
        decompressed = gzip.decompress(compressed).decode('utf-8')
        
        # The decompressed content should contain our original command
        assert large_content in decompressed
    
    def test_runtime_monitoring_edge_cases(self, builder):
        """Test runtime monitoring configuration edge cases."""
        # Zero hours
        config_zero = TaskConfig(
            name="zero-hours",
            instance_type="cpu.small",
            command="echo hello",
            max_run_time_hours=0
        )
        
        script_zero = builder.build(config_zero)
        assert script_zero.is_valid
        
        # Fractional hours
        config_fraction = TaskConfig(
            name="fraction-hours",
            instance_type="cpu.small",
            command="echo hello",
            max_run_time_hours=0.5,  # 30 minutes
            min_run_time_hours=0.25   # 15 minutes
        )
        
        script_fraction = builder.build(config_fraction)
        assert script_fraction.is_valid
        
        # Very large hours
        config_large = TaskConfig(
            name="large-hours",
            instance_type="cpu.small",
            command="echo hello",
            max_run_time_hours=8760  # 1 year
        )
        
        script_large = builder.build(config_large)
        assert script_large.is_valid
    
    def test_code_upload_edge_cases(self, builder):
        """Test code upload configuration edge cases."""
        # Upload with various paths
        upload_paths = [
            "/",  # Root directory
            ".",  # Current directory
            "..",  # Parent directory
            "/path/with spaces/",
            "/path/with/unicode/文档/",
            "relative/path",
            "./relative/path",
            "../relative/path",
        ]
        
        for path in upload_paths:
            config = TaskConfig(
                name="upload-test",
                instance_type="cpu.small",
                command="echo hello",
                upload_code=path
            )
            
            script = builder.build(config)
            assert script.is_valid
    
    def test_malformed_config_handling(self, builder):
        """Test handling of malformed configurations."""
        # Test with mock that returns unexpected values
        with patch.object(TaskConfig, 'model_dump', return_value=None):
            config = TaskConfig(
                name="malformed",
                instance_type="cpu.small",
                command="echo hello"
            )
            
            # Should handle gracefully
            script = builder.build(config)
    
    def test_script_section_ordering(self, builder):
        """Test that script sections appear in correct order."""
        config = TaskConfig(
            name="ordering-test",
            instance_type="gpu.a100",
            command="python train.py",
            image="pytorch:latest",
            env={"KEY": "value"},
            volumes=[Volume(local="/data", remote="/mnt/data", read_only=False)],
            upload_code="/workspace"
        )
        
        script = builder.build(config)
        assert script.is_valid
        
        if not script.compressed:
            content = script.content
            # Verify sections appear in expected order
            shebang_pos = content.find("#!/bin/bash")
            env_pos = content.find("export KEY=")
            volume_pos = content.find("mkdir -p /mnt/data")
            docker_pos = content.find("docker run")
            
            # Basic ordering checks (when found)
            if shebang_pos >= 0:
                assert shebang_pos == 0  # Should be first
            if env_pos >= 0 and docker_pos >= 0:
                assert env_pos < docker_pos  # Env before docker
            if volume_pos >= 0 and docker_pos >= 0:
                assert volume_pos < docker_pos  # Volumes before docker
    
    def test_error_propagation(self, builder):
        """Test that validation errors are properly propagated."""
        # Create a config that will trigger validation errors
        # by mocking a validation failure
        with patch.object(builder, '_validate_sections', return_value=["Test error 1", "Test error 2"]):
            config = TaskConfig(
                name="error-test",
                instance_type="cpu.small",
                command="echo hello"
            )
            
            script = builder.build(config)
            assert not script.is_valid
            assert len(script.validation_errors) == 2
            assert "Test error 1" in script.validation_errors
            assert "Test error 2" in script.validation_errors
            assert script.content == ""  # No content on validation failure


class TestGzipCompressor:
    """Test the GzipCompressor specifically."""
    
    def test_compression_determinism(self):
        """Test that compression is deterministic."""
        compressor = GzipCompressor()
        content = "Hello world! " * 1000
        
        compressed1 = compressor.compress(content)
        compressed2 = compressor.compress(content)
        
        # Should produce identical output
        assert compressed1 == compressed2
    
    def test_compression_ratio(self):
        """Test that compression achieves reasonable ratios."""
        compressor = GzipCompressor()
        
        # Highly compressible content (repeated text)
        repeated = "Hello world! " * 10000
        compressed_repeated = compressor.compress(repeated)
        ratio_repeated = len(compressed_repeated.encode('utf-8')) / len(repeated.encode('utf-8'))
        assert ratio_repeated < 0.1  # Should compress to less than 10%
        
        # Random content (less compressible)
        import random
        import string
        random_content = ''.join(random.choices(string.ascii_letters + string.digits, k=10000))
        compressed_random = compressor.compress(random_content)
        ratio_random = len(compressed_random.encode('utf-8')) / len(random_content.encode('utf-8'))
        assert ratio_random > 0.5  # Random data doesn't compress as well
    
    def test_empty_content_compression(self):
        """Test compressing empty content."""
        compressor = GzipCompressor()
        compressed = compressor.compress("")
        
        # Should still produce valid bootstrap script
        assert "#!/bin/bash" in compressed
        assert "base64 -d | gunzip | bash" in compressed
    
    def test_unicode_content_compression(self):
        """Test compressing Unicode content."""
        compressor = GzipCompressor()
        unicode_content = "Hello 世界! مرحبا 🌍" * 1000
        
        compressed = compressor.compress(unicode_content)
        
        # Extract and verify decompression
        import re
        match = re.search(r'echo "([^"]+)" \| base64 -d \| gunzip', compressed)
        assert match
        
        encoded = match.group(1)
        compressed_bytes = base64.b64decode(encoded)
        decompressed = gzip.decompress(compressed_bytes).decode('utf-8')
        
        assert decompressed == unicode_content


class TestStartupScriptMetadata:
    """Test script metadata generation."""
    
    def test_metadata_completeness(self):
        """Test that metadata contains expected information."""
        builder = FCPStartupScriptBuilder()
        config = TaskConfig(
            name="metadata-test",
            instance_type="gpu.a100",
            command="python train.py",
            env={"KEY": "value"},
            volumes=[Volume(local="/data", remote="/mnt/data", read_only=False)]
        )
        
        script = builder.build(config)
        
        assert script.metadata is not None
        assert "config" in script.metadata
        assert "original_size" in script.metadata
        assert "section_count" in script.metadata
        
        # Verify config is properly serialized
        assert script.metadata["config"]["name"] == "metadata-test"
        assert script.metadata["config"]["instance_type"] == "gpu.a100"
    
    def test_section_tracking(self):
        """Test that included sections are tracked."""
        builder = FCPStartupScriptBuilder()
        config = TaskConfig(
            name="section-tracking",
            instance_type="cpu.small",
            command="echo hello"
        )
        
        script = builder.build(config)
        
        assert script.sections is not None
        assert len(script.sections) > 0
        assert "header" in script.sections  # Header should always be included
        
        # When docker is used, docker section should be included
        if config.image or config.command:
            assert "docker" in script.sections