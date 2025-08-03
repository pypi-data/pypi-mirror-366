"""Tests for SSH key manager security enhancements."""

from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

from flow.providers.fcp.resources.ssh import SSHKeyManager


class TestSSHKeyManagerSecurity:
    """Test SSH key manager security features."""

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client."""
        client = Mock()
        client.request = MagicMock()
        return client

    @pytest.fixture
    def ssh_key_manager(self, mock_http_client):
        """Create an SSH key manager instance."""
        return SSHKeyManager(http_client=mock_http_client, project_id="test-project")

    def test_try_create_default_key_secure_permissions(self, ssh_key_manager, tmp_path, monkeypatch):
        """Test SSH key creation with secure permissions."""
        # Create test keys with secure permissions
        private_key = tmp_path / ".ssh" / "id_rsa"
        public_key = tmp_path / ".ssh" / "id_rsa.pub"

        private_key.parent.mkdir(parents=True)
        private_key.touch()
        private_key.chmod(0o600)  # Secure permissions

        public_key.write_text("ssh-rsa AAAAB3NzaC1yc2E... test@example.com")

        # Mock home directory
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        # Mock create_key to return a key ID
        ssh_key_manager.create_key = Mock(return_value="key-123")

        # Should succeed
        result = ssh_key_manager._try_create_default_key()

        assert result == "key-123"
        ssh_key_manager.create_key.assert_called_once()
        call_args = ssh_key_manager.create_key.call_args
        assert "flow-default-id_rsa" in call_args[0][0]
        assert "ssh-rsa AAAAB3NzaC1yc2E..." in call_args[0][1]

    def test_try_create_default_key_insecure_permissions(self, ssh_key_manager, tmp_path, monkeypatch):
        """Test SSH key creation with insecure permissions."""
        # Create test keys with insecure permissions
        private_key = tmp_path / ".ssh" / "id_rsa"
        public_key = tmp_path / ".ssh" / "id_rsa.pub"

        private_key.parent.mkdir(parents=True)
        private_key.touch()
        private_key.chmod(0o644)  # Insecure permissions!

        public_key.write_text("ssh-rsa AAAAB3NzaC1yc2E... test@example.com")

        # Mock home directory
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        # Mock create_key and auto_generate_key
        ssh_key_manager.create_key = Mock(return_value="key-123")
        ssh_key_manager.auto_generate_key = Mock(return_value=None)  # Simulate auto-generation failure

        # Should skip this key due to insecure permissions
        result = ssh_key_manager._try_create_default_key()

        # The behavior we care about: key is skipped due to insecure permissions
        assert result is None
        ssh_key_manager.create_key.assert_not_called()
        # But auto_generate_key should be called as a fallback
        ssh_key_manager.auto_generate_key.assert_called_once()

    def test_fcp_ssh_key_env_private_key(self, ssh_key_manager, tmp_path, monkeypatch):
        """Test FCP_SSH_KEY environment variable with private key path."""
        # Create test keys
        private_key = tmp_path / "my_key"
        public_key = tmp_path / "my_key.pub"

        private_key.touch()
        private_key.chmod(0o600)  # Secure permissions
        public_key.write_text("ssh-rsa AAAAB3NzaC1yc2E... test@example.com")

        # Set environment variable to private key
        monkeypatch.setenv("FCP_SSH_KEY", str(private_key))

        # Mock create_key
        ssh_key_manager.create_key = Mock(return_value="key-456")

        result = ssh_key_manager._try_create_default_key()

        assert result == "key-456"
        ssh_key_manager.create_key.assert_called_once_with(
            "flow-fcp-key",
            "ssh-rsa AAAAB3NzaC1yc2E... test@example.com"
        )

    def test_fcp_ssh_key_env_public_key(self, ssh_key_manager, tmp_path, monkeypatch):
        """Test FCP_SSH_KEY environment variable with public key path."""
        # Create test public key
        public_key = tmp_path / "my_key.pub"
        public_key.write_text("ssh-rsa AAAAB3NzaC1yc2E... test@example.com")

        # Set environment variable to public key
        monkeypatch.setenv("FCP_SSH_KEY", str(public_key))

        # Mock create_key
        ssh_key_manager.create_key = Mock(return_value="key-789")

        result = ssh_key_manager._try_create_default_key()

        assert result == "key-789"
        ssh_key_manager.create_key.assert_called_once_with(
            "flow-fcp-key",
            "ssh-rsa AAAAB3NzaC1yc2E... test@example.com"
        )

    def test_fcp_ssh_key_env_insecure_permissions(self, ssh_key_manager, tmp_path, monkeypatch):
        """Test FCP_SSH_KEY with insecure private key permissions."""
        # Create test keys with insecure permissions
        private_key = tmp_path / "insecure_key"
        public_key = tmp_path / "insecure_key.pub"

        private_key.touch()
        private_key.chmod(0o644)  # Insecure!
        public_key.write_text("ssh-rsa AAAAB3NzaC1yc2E... test@example.com")

        # Set environment variable
        monkeypatch.setenv("FCP_SSH_KEY", str(private_key))

        # Mock create_key and auto_generate_key
        ssh_key_manager.create_key = Mock()
        ssh_key_manager.auto_generate_key = Mock(return_value=None)  # Simulate auto-generation failure

        # Should fail due to insecure permissions
        result = ssh_key_manager._try_create_default_key()

        # The behavior we care about: no key created due to insecure permissions
        assert result is None
        ssh_key_manager.create_key.assert_not_called()
        # But auto_generate_key should be called as a fallback
        ssh_key_manager.auto_generate_key.assert_called_once()

    def test_fcp_ssh_key_env_missing_file(self, ssh_key_manager, monkeypatch):
        """Test FCP_SSH_KEY with non-existent file."""
        # Set environment variable to non-existent file
        monkeypatch.setenv("FCP_SSH_KEY", "/path/to/nonexistent/key")

        # Mock create_key and auto_generate_key
        ssh_key_manager.create_key = Mock()
        ssh_key_manager.auto_generate_key = Mock(return_value=None)  # Simulate auto-generation failure

        result = ssh_key_manager._try_create_default_key()

        # The behavior we care about: no key created when file doesn't exist
        assert result is None
        ssh_key_manager.create_key.assert_not_called()
        # But auto_generate_key should be called as a fallback
        ssh_key_manager.auto_generate_key.assert_called_once()

    def test_flow_ssh_public_key_env(self, ssh_key_manager, monkeypatch):
        """Test FCP_SSH_PUBLIC_KEY environment variable."""
        # Set environment variable with public key content
        monkeypatch.setenv("FCP_SSH_PUBLIC_KEY", "ssh-rsa AAAAB3NzaC1yc2E... env@example.com")

        # Mock create_key
        ssh_key_manager.create_key = Mock(return_value="key-env")

        result = ssh_key_manager._try_create_default_key()

        assert result == "key-env"
        ssh_key_manager.create_key.assert_called_once_with(
            "flow-env-key",
            "ssh-rsa AAAAB3NzaC1yc2E... env@example.com"
        )

    def test_ensure_keys_with_permission_check(self, ssh_key_manager, tmp_path, monkeypatch):
        """Test ensure_keys integrates permission checking."""
        # Mock empty existing keys
        ssh_key_manager.list_keys = Mock(return_value=[])

        # Create secure key
        private_key = tmp_path / ".ssh" / "id_rsa"
        public_key = tmp_path / ".ssh" / "id_rsa.pub"

        private_key.parent.mkdir(parents=True)
        private_key.touch()
        private_key.chmod(0o600)
        public_key.write_text("ssh-rsa AAAAB3NzaC1yc2E... test@example.com")

        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        ssh_key_manager.create_key = Mock(return_value="key-auto")

        # Ensure keys should create one
        result = ssh_key_manager.ensure_keys()

        assert result == ["key-auto"]
        ssh_key_manager.create_key.assert_called_once()
