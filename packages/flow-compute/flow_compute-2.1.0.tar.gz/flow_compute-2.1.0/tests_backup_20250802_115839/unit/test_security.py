"""Tests for security utilities."""

from pathlib import Path

import pytest

from flow.errors import ValidationError
from flow.utils.security import (
    check_ssh_key_permissions,
    sanitize_command,
    sanitize_path,
    validate_instance_id,
    validate_project_id,
)


class TestSecurityUtils:
    """Test security utility functions."""

    def test_sanitize_path_valid_paths(self):
        """Test path sanitization with valid paths."""
        # Absolute path
        result = sanitize_path("/home/user/data.txt")
        assert isinstance(result, Path)
        assert result.is_absolute()

        # Relative path that's safe
        result = sanitize_path("data/model.pkl")
        assert isinstance(result, Path)
        assert result.is_absolute()  # resolve() makes it absolute

        # Path with spaces
        result = sanitize_path("my data/file.txt")
        assert isinstance(result, Path)

    def test_sanitize_path_traversal_attempts(self):
        """Test path sanitization blocks traversal attempts."""
        # Direct traversal
        with pytest.raises(ValidationError, match="Path traversal detected"):
            sanitize_path("../../../etc/passwd")

        # Sneaky traversal
        with pytest.raises(ValidationError, match="Path traversal detected"):
            sanitize_path("data/../../../etc/passwd")

        # Mixed traversal
        with pytest.raises(ValidationError, match="Path traversal detected"):
            sanitize_path("./../../sensitive")

    def test_sanitize_command(self):
        """Test command escaping."""
        # Simple command
        assert sanitize_command("python train.py") == "'python train.py'"

        # Command with spaces
        assert sanitize_command("python my script.py") == "'python my script.py'"

        # Command with special characters
        result = sanitize_command("echo $HOME")
        assert "$" not in result or result == "'echo $HOME'"

        # Potential injection
        result = sanitize_command("python train.py; rm -rf /")
        assert ";" not in result or result.startswith("'") and result.endswith("'")

    def test_check_ssh_key_permissions_secure(self, tmp_path):
        """Test SSH key permission check for secure keys."""
        # Create a test key with secure permissions
        key_path = tmp_path / "id_rsa"
        key_path.touch()
        key_path.chmod(0o600)

        # Should not raise
        check_ssh_key_permissions(key_path)

        # Also test 400 (read-only)
        key_path.chmod(0o400)
        check_ssh_key_permissions(key_path)

    def test_check_ssh_key_permissions_insecure(self, tmp_path):
        """Test SSH key permission check catches insecure keys."""
        # Create a test key with insecure permissions
        key_path = tmp_path / "id_rsa"
        key_path.touch()

        # Test various insecure permissions
        for mode in [0o644, 0o664, 0o777, 0o755]:
            key_path.chmod(mode)
            with pytest.raises(ValidationError, match="insecure permissions"):
                check_ssh_key_permissions(key_path)

    def test_check_ssh_key_permissions_missing_file(self, tmp_path):
        """Test SSH key permission check with missing file."""
        key_path = tmp_path / "nonexistent"

        with pytest.raises(ValidationError, match="SSH key not found"):
            check_ssh_key_permissions(key_path)

    def test_validate_instance_id(self):
        """Test FCP instance ID validation."""
        # Valid FCP formats (based on actual codebase examples)
        assert validate_instance_id("inst-abc123") == "inst-abc123"
        assert validate_instance_id("inst-7f9c4d2a") == "inst-7f9c4d2a"
        assert validate_instance_id("bid-test-12345678") == "bid-test-12345678"

        # Invalid formats - SQL injection
        with pytest.raises(ValidationError, match="Invalid instance ID format"):
            validate_instance_id("inst-123; DROP TABLE")

        # Invalid formats - path traversal
        with pytest.raises(ValidationError, match="Invalid instance ID format"):
            validate_instance_id("../../etc/passwd")

        # Invalid formats - special characters
        with pytest.raises(ValidationError, match="Invalid instance ID format"):
            validate_instance_id("inst@malicious.com")

    def test_validate_project_id(self):
        """Test FCP project ID validation."""
        # Valid FCP formats (from actual test data)
        assert validate_project_id("project-123") == "project-123"
        assert validate_project_id("test-project") == "test-project"
        assert validate_project_id("ml_training_2024") == "ml_training_2024"

        # Invalid formats - SQL injection
        with pytest.raises(ValidationError, match="Invalid project ID format"):
            validate_project_id("project; DROP TABLE")

        # Invalid formats - path traversal
        with pytest.raises(ValidationError, match="Invalid project ID format"):
            validate_project_id("../../../etc")

        # Invalid formats - special characters
        with pytest.raises(ValidationError, match="Invalid project ID format"):
            validate_project_id("project@hack.com")
