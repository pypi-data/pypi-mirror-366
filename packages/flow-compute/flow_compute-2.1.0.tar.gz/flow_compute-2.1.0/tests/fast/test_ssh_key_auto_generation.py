"""Unit tests for SSH key auto-generation functionality.

Verifies the automatic SSH key generation feature including:
- Key generation when no keys exist
- Reuse of previously generated keys
- Graceful fallback on failures
- Secure permission handling
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from flow.providers.fcp.resources.ssh import SSHKeyManager


class TestSSHKeyAutoGeneration:
    """Test suite for SSH key auto-generation features.
    
    Comprehensive tests covering key generation, caching, error handling,
    and integration with the FCP API.
    """

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client for API interactions.
        
        Returns:
            Mock: Configured mock with request method.
        """
        client = Mock()
        client.request = MagicMock()
        return client

    @pytest.fixture
    def ssh_key_manager(self, mock_http_client):
        """Create an SSH key manager instance for testing.
        
        Args:
            mock_http_client: Mocked HTTP client fixture.
            
        Returns:
            SSHKeyManager: Configured instance with test project.
        """
        return SSHKeyManager(http_client=mock_http_client, project_id="test-project")

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_auto_generation(self, mock_which, mock_run, ssh_key_manager, tmp_path, monkeypatch):
        """Verify SSH key generation succeeds when no existing keys are found.
        
        Ensures that when a user has no SSH keys, the system automatically
        generates an ed25519 key pair and registers it with the FCP API.
        """
        mock_which.return_value = '/usr/bin/ssh-keygen'
        mock_run.return_value.returncode = 0

        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        key_dir = tmp_path / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)

        ssh_key_manager.http.request.return_value = {
            "fid": "ssh-key_123",
            "name": "flow-auto-123456",
            "public_key": "ssh-ed25519 AAAAC3...",
            "project": "test-project",
            "created_at": "2024-01-15T10:00:00Z"
        }

        # Intercept subprocess.run to simulate ssh-keygen behavior
        def mock_subprocess_run(cmd, **kwargs):
            if 'ssh-keygen' in cmd:
                # Extract output path from command
                key_path = Path(cmd[cmd.index('-f') + 1])
                # Simulate ssh-keygen creating files
                key_path.touch(mode=0o600)
                key_path.with_suffix('.pub').write_text("ssh-ed25519 AAAAC3... flow-auto@test")
            return Mock(returncode=0)

        mock_run.side_effect = mock_subprocess_run

        result = ssh_key_manager._generate_ssh_key()

        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == 'ssh-keygen'
        assert call_args[call_args.index('-t') + 1] == 'ed25519'
        assert mock_run.call_args.kwargs['timeout'] == 30

    @patch('shutil.which')
    def test_missing_ssh_keygen(self, mock_which, ssh_key_manager):
        """Verify graceful fallback when ssh-keygen binary is not available.
        
        When ssh-keygen is missing from the system PATH, key generation
        should return None without raising exceptions.
        """
        mock_which.return_value = None

        result = ssh_key_manager._generate_ssh_key()

        assert result is None
        assert not ssh_key_manager.http.request.called

    def test_key_reuse(self, ssh_key_manager, tmp_path, monkeypatch):
        """Verify previously generated keys are reused for the same project.
        
        Keys generated for a project should be persisted in metadata and
        reused on subsequent calls to avoid unnecessary regeneration.
        """
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        key_dir = tmp_path / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "ssh-key_existing": {
                "key_id": "ssh-key_existing",
                "key_name": "flow-auto-123456",
                "private_key_path": str(key_dir / "flow-auto-123456"),
                "created_at": "2024-01-15T10:00:00Z",
                "project": "test-project",
                "auto_generated": True
            }
        }

        metadata_path = key_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        result = ssh_key_manager._get_cached_auto_key()

        assert result == "ssh-key_existing"

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_api_failure_handling(self, mock_which, mock_run, ssh_key_manager, tmp_path, monkeypatch):
        """Verify key generation fails gracefully when API is unavailable.
        
        When the FCP API returns an error during key registration, the
        generation process should return None without propagating exceptions.
        """
        mock_which.return_value = '/usr/bin/ssh-keygen'
        mock_run.return_value.returncode = 0
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        key_dir = tmp_path / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)
        public_key_path = key_dir / "flow-auto-1234567890.pub"
        public_key_path.write_text("ssh-ed25519 AAAAC3... flow-auto@test")

        ssh_key_manager.http.request.side_effect = Exception("API error")

        result = ssh_key_manager._generate_ssh_key()

        assert result is None

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_subprocess_failure(self, mock_which, mock_run, ssh_key_manager):
        """Verify proper handling when ssh-keygen subprocess fails.
        
        When ssh-keygen returns a non-zero exit code, key generation
        should fail gracefully without making API calls.
        """
        mock_which.return_value = '/usr/bin/ssh-keygen'
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Permission denied"

        result = ssh_key_manager._generate_ssh_key()

        assert result is None
        assert not ssh_key_manager.http.request.called

    def test_metadata_persistence(self, ssh_key_manager, tmp_path):
        """Verify metadata is correctly stored for generated keys.
        
        Generated key metadata should be persisted to JSON with proper
        structure including project ID, timestamps, and file paths.
        """
        key_id = "ssh-key_123"
        key_name = "flow-auto-123456"
        private_path = tmp_path / "flow-auto-123456"
        private_path.touch()

        ssh_key_manager._store_key_metadata(key_id, key_name, private_path)

        metadata_path = tmp_path / "metadata.json"
        assert metadata_path.exists()

        metadata = json.loads(metadata_path.read_text())
        assert key_id in metadata
        assert metadata[key_id]["key_name"] == key_name
        assert metadata[key_id]["private_key_path"] == str(private_path)
        assert metadata[key_id]["project"] == "test-project"
        assert metadata[key_id]["auto_generated"] is True
        assert "created_at" in metadata[key_id]

    def test_file_permissions(self, ssh_key_manager, tmp_path):
        """Verify SSH keys are created with secure file permissions.
        
        Private keys must have 0600 permissions to prevent unauthorized
        access as required by SSH security standards.
        """
        test_file = tmp_path / "test_key"
        test_file.touch()

        ssh_key_manager._set_key_permissions(test_file)

        mode = test_file.stat().st_mode & 0o777
        assert mode == 0o600

    @patch('random.randint')
    @patch('subprocess.run')
    @patch('shutil.which')
    @patch('time.time')
    def test_complete_flow(self, mock_time, mock_which, mock_run, mock_randint, ssh_key_manager, tmp_path, monkeypatch):
        """Verify complete SSH key generation flow from ensure_keys.
        
        Tests the full integration within the unit test environment,
        ensuring all components work together correctly when no keys exist.
        """
        mock_which.return_value = '/usr/bin/ssh-keygen'
        mock_time.return_value = 1234567890
        mock_randint.return_value = 5678
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        ssh_key_manager.list_keys = Mock(return_value=[])

        key_dir = tmp_path / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)

        def mock_subprocess_run(cmd, **kwargs):
            if 'ssh-keygen' in cmd:
                key_path = Path(cmd[cmd.index('-f') + 1])
                key_path.touch(mode=0o600)
                key_path.with_suffix('.pub').write_text("ssh-ed25519 AAAAC3... flow-auto@test")
            return Mock(returncode=0)

        mock_run.side_effect = mock_subprocess_run

        # Mock server-side key generation response
        ssh_key_manager.http.request.side_effect = [
            # First call: POST to generate server-side key
            {
                "fid": "ssh-key_auto",
                "name": "flow-auto-1234567890-5678",
                "public_key": "ssh-ed25519 AAAAC3...",
                "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1...",
                "project": "test-project",
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]

        # Call auto_generate_key directly to test the full flow
        result = ssh_key_manager.auto_generate_key()

        assert result == "ssh-key_auto"
        # Server-side generation should not call subprocess.run
        assert not mock_run.called
        assert ssh_key_manager.http.request.called

    def test_project_key_selection(self, ssh_key_manager, tmp_path, monkeypatch):
        """Verify most recent key is selected when multiple exist for a project.
        
        When multiple auto-generated keys exist for a project in metadata,
        the system should return the most recently created one.
        """
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)

        key_dir = tmp_path / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "ssh-key_old": {
                "key_id": "ssh-key_old",
                "created_at": "2024-01-10T10:00:00Z",
                "project": "test-project",
                "auto_generated": True
            },
            "ssh-key_new": {
                "key_id": "ssh-key_new",
                "created_at": "2024-01-15T10:00:00Z",
                "project": "test-project",
                "auto_generated": True
            },
            "ssh-key_other": {
                "key_id": "ssh-key_other",
                "created_at": "2024-01-20T10:00:00Z",
                "project": "other-project",
                "auto_generated": True
            }
        }

        metadata_path = key_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        result = ssh_key_manager._get_cached_auto_key()

        assert result == "ssh-key_new"
