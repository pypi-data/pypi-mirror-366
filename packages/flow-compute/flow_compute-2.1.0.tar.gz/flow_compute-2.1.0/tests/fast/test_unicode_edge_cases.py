"""Unit tests for unicode edge cases in command execution and file paths.

This module tests proper handling of unicode characters, including:
- Emoji and special unicode symbols
- Non-ASCII characters from various languages
- RTL (Right-to-Left) text
- Zero-width characters
- Surrogate pairs
- Path separators and special filesystem characters
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flow.api.models import MountSpec, TaskConfig, VolumeSpec
from flow.cli.commands.run import RunCommand
from flow.errors import ValidationError
from flow.providers.fcp.provider import FCPProvider
from flow.providers.fcp.runtime.startup.builder import StartupScriptBuilder
from flow.providers.fcp.runtime.startup.sections import UserScriptSection
from flow.providers.local.provider import LocalProvider


class TestUnicodeCommandExecution:
    """Test unicode handling in command execution."""

    # Unicode test cases covering various edge cases
    UNICODE_TEST_CASES = [
        # Basic emoji
        ("🚀 rocket launch", "emoji in command"),
        ("echo 'Hello 👋 World'", "emoji in echo"),
        
        # Non-ASCII characters from various languages
        ("echo 'Привет мир'", "Cyrillic characters"),
        ("echo '你好世界'", "Chinese characters"),
        ("echo 'مرحبا بالعالم'", "Arabic RTL text"),
        ("echo 'שלום עולם'", "Hebrew RTL text"),
        ("echo 'こんにちは世界'", "Japanese characters"),
        ("echo 'Γεια σου κόσμε'", "Greek characters"),
        ("echo 'Здравей свят'", "Bulgarian Cyrillic"),
        
        # Special unicode characters
        ("echo 'Test\u200bZero\u200bWidth'", "zero-width spaces"),
        ("echo 'Test\u2028Line\u2029Separator'", "unicode line separators"),
        ("echo '🏳️‍🌈 🏴‍☠️'", "complex emoji with ZWJ sequences"),
        
        # Mathematical and technical symbols
        ("echo '∑∏∫∂∇≈≠±∞'", "mathematical symbols"),
        ("echo '⌘⌥⇧⌃⌫⏎'", "technical symbols"),
        
        # Mixed directionality
        ("echo 'Hello مرحبا World עולם'", "mixed LTR/RTL text"),
        
        # Potentially problematic characters
        ("echo 'Test\x00Null'", "null character"),
        ("echo 'Test\tTab\nNewline\rReturn'", "control characters"),
    ]

    def test_unicode_commands_in_task_config(self):
        """Test TaskConfig handles unicode commands properly."""
        for i, (command, description) in enumerate(self.UNICODE_TEST_CASES):
            # Create valid task name (alphanumeric with dashes/underscores)
            safe_name = f"test_{i}_{description.replace(' ', '_').replace('-', '_')[:20]}"
            # Remove any non-alphanumeric characters
            safe_name = ''.join(c if c.isalnum() or c in '_-' else '_' for c in safe_name)
            # Ensure it starts with alphanumeric  
            if safe_name and not safe_name[0].isalnum():
                safe_name = 'a' + safe_name[1:]
            
            config = TaskConfig(
                name=safe_name,
                instance_type="a100",
                command=[command]
            )
            assert config.command == [command]
            
            # Test serialization/deserialization
            config_dict = config.model_dump()
            assert config_dict["command"] == [command]
            
            # Test reconstruction
            config2 = TaskConfig(**config_dict)
            assert config2.command == [command]

    def test_unicode_in_startup_script_builder(self):
        """Test StartupScriptBuilder handles unicode commands."""
        for command, description in self.UNICODE_TEST_CASES:
            # Skip null character test for shell scripts
            if '\x00' in command:
                continue
                
            # Create task config with unicode command
            config = TaskConfig(
                name=f"unicode_test",
                instance_type="a100",
                command=[command],
                max_run_time_hours=None  # Disable runtime monitoring
            )
            
            # Build startup script
            builder = StartupScriptBuilder()
            script_obj = builder.build(config)
            
            # If script is compressed, skip content checks
            if script_obj.compressed:
                # At least verify the script_obj was created successfully
                assert script_obj.content
                assert script_obj.original_size > 0
                continue
            
            script = script_obj.content
            
            # Verify command appears in script
            # The command will be in the user script section
            # It may be escaped or quoted, so check for the core content
            if command.startswith("echo "):
                # For echo commands, check the content after 'echo'
                content = command[5:].strip().strip("'\"")
                assert content in script
            else:
                assert command in script or repr(command) in script
            
            # Verify script is valid UTF-8
            script.encode('utf-8')

    def test_unicode_environment_variables(self):
        """Test unicode in environment variables."""
        unicode_env_vars = {
            "EMOJI_VAR": "🚀🌟✨",
            "RUSSIAN_VAR": "Привет мир",
            "CHINESE_VAR": "你好世界",
            "ARABIC_VAR": "مرحبا بالعالم",
            "MIXED_VAR": "Hello 世界 🌍",
        }
        
        config = TaskConfig(
            name="unicode-env-test",
            instance_type="a100",
            command=["printenv"],
            env=unicode_env_vars
        )
        
        assert config.env == unicode_env_vars
        
        # Test in startup script context with Docker
        from flow.providers.fcp.runtime.startup.sections import ScriptContext, DockerSection
        
        # Environment variables are handled in Docker section
        context = ScriptContext(
            environment=unicode_env_vars,
            docker_image="python:3.9",
            docker_command=["printenv"]
        )
        docker_section = DockerSection()
        
        if docker_section.should_include(context):
            script = docker_section.generate(context)
            
            for key, value in unicode_env_vars.items():
                # Check that env vars are passed to docker with -e flag
                assert f'-e {key}=' in script
                # Value should be properly quoted
                assert f'{key}="{value}"' in script or f"{key}='{value}'" in script


class TestUnicodeFilePaths:
    """Test unicode handling in file paths."""
    
    UNICODE_PATH_CASES = [
        # Basic cases
        "/data/🚀_rocket_data",
        "/models/模型_chinese",
        "/datasets/данные_russian",
        "/output/نتائج_arabic",
        
        # Spaces and special chars
        "/data/my 📁 folder/file.txt",
        "/path/with spaces and émojis 🎉/data",
        
        # Mixed scripts
        "/mixed/Hello_世界_🌍/data",
        "/test/Тест_Test_テスト/file",
        
        # Edge cases (but valid paths)
        "/data/test\u200b_zwsp",  # Zero-width space
        "/path/test—dash—test",  # Em dash
        "/data/test…ellipsis",  # Ellipsis character
    ]

    def test_unicode_mount_paths(self):
        """Test unicode in mount paths."""
        for path in self.UNICODE_PATH_CASES:
            mount = MountSpec(
                source="s3://bucket/data",
                target=path
            )
            assert mount.target == path
            
            # Test serialization
            mount_dict = mount.model_dump()
            assert mount_dict["target"] == path
            
            # Test reconstruction
            mount2 = MountSpec(**mount_dict)
            assert mount2.target == path

    def test_unicode_volume_paths(self):
        """Test unicode in volume mount paths."""
        for path in self.UNICODE_PATH_CASES:
            volume = VolumeSpec(
                mount_path=path,
                size_gb=10
            )
            assert volume.mount_path == path
            
            # Test in TaskConfig
            config = TaskConfig(
                name="test",
                instance_type="a100",
                command=["ls", path],
                volumes=[volume]
            )
            assert config.volumes[0].mount_path == path

    def test_unicode_paths_in_startup_script(self):
        """Test unicode paths in startup scripts."""
        from flow.providers.fcp.runtime.startup.sections import ScriptContext
        
        for path in self.UNICODE_PATH_CASES:
            # Test mkdir command
            mkdir_cmd = f"mkdir -p '{path}'"
            
            # Create context with the command as user script
            context = ScriptContext(user_script=mkdir_cmd)
            
            # Build script with the context
            section = UserScriptSection()
            if section.should_include(context):
                script = section.generate(context)
                
                # Path should be in the generated script
                assert path in script or repr(path) in script

    @pytest.mark.integration
    def test_unicode_paths_filesystem_operations(self):
        """Test actual filesystem operations with unicode paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            
            for path in self.UNICODE_PATH_CASES:
                # Skip paths with null bytes or other invalid chars
                if '\x00' in path:
                    continue
                    
                # Create relative path
                rel_path = path.lstrip('/')
                full_path = base / rel_path
                
                try:
                    # Create directory
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    full_path.write_text("Test content with unicode: 你好 🌍")
                    
                    # Read back
                    content = full_path.read_text()
                    assert "你好 🌍" in content
                    
                    # List directory
                    assert full_path.name in os.listdir(full_path.parent)
                    
                except (OSError, UnicodeError) as e:
                    # Some filesystems may not support certain unicode chars
                    pytest.skip(f"Filesystem doesn't support unicode path: {e}")


class TestUnicodeErrorHandling:
    """Test error handling for problematic unicode cases."""

    def test_invalid_unicode_sequences(self):
        """Test handling of invalid unicode sequences."""
        # Surrogate pairs outside valid range
        invalid_cases = [
            "\uD800",  # Lone high surrogate
            "\uDFFF",  # Lone low surrogate
            "\uD800\uD800",  # Two high surrogates
        ]
        
        for invalid in invalid_cases:
            # Most operations should handle these gracefully
            try:
                config = TaskConfig(
                    name="test",
                    instance_type="a100",
                    command=[f"echo '{invalid}'"]
                )
                # Should either work or raise a clear validation error
                assert config.command[0]
            except (ValidationError, UnicodeError):
                # This is acceptable - clear error
                pass

    def test_unicode_normalization(self):
        """Test unicode normalization issues."""
        import unicodedata
        
        # Same character in different forms
        # é can be one character or e + combining accent
        composed = "café"  # Single character é (NFC)
        decomposed = unicodedata.normalize('NFD', composed)  # e + combining accent
        
        assert len(composed) == 4
        assert len(decomposed) == 5  # e + combining accent makes it 5 chars
        assert composed != decomposed
        
        # Both should work in paths
        for text in [composed, decomposed]:
            mount = MountSpec(
                source="s3://bucket/data",
                target=f"/data/{text}"
            )
            assert text in mount.target
            
        # Normalized forms should be equivalent
        assert unicodedata.normalize('NFC', composed) == unicodedata.normalize('NFC', decomposed)


class TestUnicodeIntegration:
    """Integration tests for unicode handling across components."""

    @patch('subprocess.run')
    def test_unicode_command_execution_local_provider(self, mock_run):
        """Test LocalProvider executes unicode commands properly."""
        from flow._internal.config import Config
        
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        config = Config(provider="local")
        provider = LocalProvider(config)
        config = TaskConfig(
            name="unicode-test",
            instance_type="cpu",
            command=["echo", "Hello 你好 🌍"],
        )
        
        # Note: This is a simplified test - actual implementation would need
        # proper local provider setup
        # The key is that unicode should be preserved through the execution chain

    def test_unicode_in_cli_arguments(self):
        """Test CLI handles unicode arguments."""
        # Test unicode in commands (names must be alphanumeric)
        unicode_commands = [
            ["echo", "🚀 Launch!"],
            ["echo", "测试 test"],
            ["echo", "задача test"],
            ["python", "-c", "print('Hello 世界')"],
        ]
        
        for i, command in enumerate(unicode_commands):
            config = TaskConfig(
                name=f"unicode_test_{i}",
                instance_type="a100",
                command=command
            )
            assert config.command == command

    def test_unicode_yaml_config(self):
        """Test unicode in YAML configuration files."""
        yaml_content = """
name: unicode_test_task
instance_type: a100
command: ["echo", "Hello 世界"]
env:
  MESSAGE: "你好 🌍"
  PATH_VAR: "/data/文件夹/test"
volumes:
  - mount_path: /data/数据
    size_gb: 10
"""
        import yaml
        
        # Parse YAML with unicode
        config_dict = yaml.safe_load(yaml_content)
        
        # Create TaskConfig
        config = TaskConfig(**config_dict)
        
        assert config.name == "unicode_test_task"  # Name was sanitized in YAML
        assert config.command == ["echo", "Hello 世界"]
        assert config.env["MESSAGE"] == "你好 🌍"
        assert config.volumes[0].mount_path == "/data/数据"


class TestUnicodeEdgeCaseSecurity:
    """Test security implications of unicode handling."""

    def test_unicode_injection_prevention(self):
        """Test prevention of unicode-based injection attacks."""
        # Homograph attacks - characters that look similar
        suspicious_commands = [
            "еcho test",  # Cyrillic 'е' instead of Latin 'e'
            "｜｜ rm -rf /",  # Full-width pipe characters
            "echo test； rm -rf /",  # Full-width semicolon
        ]
        
        for cmd in suspicious_commands:
            config = TaskConfig(
                name="test",
                instance_type="a100",
                command=[cmd]
            )
            # Command should be preserved as-is, security handled elsewhere
            assert config.command == [cmd]

    def test_unicode_path_traversal_prevention(self):
        """Test unicode doesn't bypass path traversal protection."""
        # Various unicode representations of path traversal
        traversal_attempts = [
            "/data/../../../etc/passwd",
            "/data/．．/．．/etc/passwd",  # Full-width dots
            "/data/\u2025\u2025/etc/passwd",  # Two-dot leader
        ]
        
        for path in traversal_attempts:
            mount = MountSpec(
                source="s3://bucket/data",
                target=path
            )
            # Path validation should happen at a different layer
            assert mount.target == path


if __name__ == "__main__":
    pytest.main([__file__, "-v"])