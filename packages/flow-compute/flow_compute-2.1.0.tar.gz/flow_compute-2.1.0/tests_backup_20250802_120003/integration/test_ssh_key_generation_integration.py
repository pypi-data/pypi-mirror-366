"""Integration tests for SSH key generation using real ssh-keygen binary.

Verifies the SSH key auto-generation feature works correctly with actual
system components, ensuring realistic behavior beyond unit test mocks.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flow.providers.fcp.resources.ssh import SSHKeyManager


class TestSSHKeyGenerationIntegration:
    """Integration tests using real ssh-keygen binary."""

    @pytest.fixture
    def temp_home(self):
        """Create a temporary home directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_http_client(self):
        """Create a mock HTTP client that simulates real API behavior."""
        client = Mock()

        created_keys = []

        def mock_request(method, url, **kwargs):
            if method == "POST" and url == "/v2/ssh-keys":
                json_data = kwargs.get('json', {})
                key_data = {
                    "fid": f"ssh-key_{hash(json_data['name']) % 1000000}",
                    "name": json_data['name'],
                    "public_key": json_data['public_key'],
                    "project": json_data['project'],
                    "created_at": "2024-01-15T10:00:00Z"
                }
                created_keys.append(key_data)
                return key_data
            elif method == "GET" and url == "/v2/ssh-keys":
                project = kwargs.get('params', {}).get('project')
                if project:
                    return [k for k in created_keys if k['project'] == project]
                return created_keys
            return []

        client.request = Mock(side_effect=mock_request)
        return client

    @pytest.mark.skipif(not shutil.which('ssh-keygen'), reason="ssh-keygen not available")
    def test_key_generation(self, mock_http_client, temp_home, monkeypatch):
        """Verify SSH key generation using real ssh-keygen binary.
        
        Ensures the complete key generation flow works with actual system
        ssh-keygen, creating proper ed25519 keys with correct permissions.
        """
        monkeypatch.setattr(Path, 'home', lambda: temp_home)

        manager = SSHKeyManager(http_client=mock_http_client, project_id="test-project")

        assert manager.list_keys() == []

        result = manager.ensure_keys()

        assert len(result) == 1
        assert result[0].startswith("ssh-key_")

        key_dir = temp_home / ".flow" / "keys"
        assert key_dir.exists()

        key_files = list(key_dir.glob("flow-auto-*"))
        private_keys = [f for f in key_files if not f.suffix]
        public_keys = [f for f in key_files if f.suffix == '.pub']

        assert len(private_keys) == 1
        assert len(public_keys) == 1

        private_key = private_keys[0]
        assert private_key.stat().st_mode & 0o777 == 0o600

        public_key_content = public_keys[0].read_text()
        assert public_key_content.startswith("ssh-ed25519 ")
        assert "flow-auto@" in public_key_content

        metadata_path = key_dir / "metadata.json"
        assert metadata_path.exists()
        metadata = json.loads(metadata_path.read_text())
        assert len(metadata) == 1
        key_id = list(metadata.keys())[0]
        assert metadata[key_id]["project"] == "test-project"
        assert metadata[key_id]["auto_generated"] is True

        assert mock_http_client.request.called
        call_args = mock_http_client.request.call_args
        assert call_args[1]['json']['public_key'] == public_key_content.strip()

    @pytest.mark.skipif(not shutil.which('ssh-keygen'), reason="ssh-keygen not available")
    def test_key_reuse(self, mock_http_client, temp_home, monkeypatch):
        """Verify existing auto-generated keys are reused.
        
        Subsequent calls to ensure_keys should return the same key ID
        without generating new keys, avoiding unnecessary key proliferation.
        """
        monkeypatch.setattr(Path, 'home', lambda: temp_home)

        manager = SSHKeyManager(http_client=mock_http_client, project_id="test-project")

        first_result = manager.ensure_keys()
        assert len(first_result) == 1
        first_key_id = first_result[0]

        manager.invalidate_cache()

        second_result = manager.ensure_keys()
        assert second_result == [first_key_id]

        metadata_path = temp_home / ".flow" / "keys" / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        assert len(metadata) == 1

    @pytest.mark.skipif(not shutil.which('ssh-keygen'), reason="ssh-keygen not available")
    def test_corrupted_metadata_recovery(self, mock_http_client, temp_home, monkeypatch):
        """Verify recovery from corrupted metadata files.
        
        When metadata.json is corrupted or malformed, the system should
        generate new keys rather than failing completely.
        """
        monkeypatch.setattr(Path, 'home', lambda: temp_home)

        key_dir = temp_home / ".flow" / "keys"
        key_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = key_dir / "metadata.json"
        metadata_path.write_text("{ invalid json")

        manager = SSHKeyManager(http_client=mock_http_client, project_id="test-project")

        result = manager.ensure_keys()
        assert len(result) == 1

        metadata = json.loads(metadata_path.read_text())
        assert len(metadata) == 1

    def test_missing_ssh_keygen(self, mock_http_client, temp_home, monkeypatch):
        """Verify behavior when ssh-keygen is not available.
        
        Systems without ssh-keygen should return empty key list without
        attempting generation, allowing manual key provisioning.
        """
        monkeypatch.setattr(Path, 'home', lambda: temp_home)

        with patch('shutil.which', return_value=None):
            manager = SSHKeyManager(http_client=mock_http_client, project_id="test-project")

            result = manager.ensure_keys()
            assert result == []

            post_calls = [call for call in mock_http_client.request.call_args_list
                         if call[1].get('method') == 'POST']
            assert len(post_calls) == 0

    @pytest.mark.skipif(not shutil.which('ssh-keygen'), reason="ssh-keygen not available")
    def test_project_isolation(self, mock_http_client, temp_home, monkeypatch):
        """Verify different projects maintain separate SSH keys.
        
        Each project should have its own auto-generated key to maintain
        proper access control and security isolation between projects.
        """
        monkeypatch.setattr(Path, 'home', lambda: temp_home)

        manager_a = SSHKeyManager(http_client=mock_http_client, project_id="project-a")
        keys_a = manager_a.ensure_keys()
        assert len(keys_a) == 1

        manager_b = SSHKeyManager(http_client=mock_http_client, project_id="project-b")
        keys_b = manager_b.ensure_keys()
        assert len(keys_b) == 1

        assert keys_a[0] != keys_b[0]

        metadata_path = temp_home / ".flow" / "keys" / "metadata.json"
        metadata = json.loads(metadata_path.read_text())
        assert len(metadata) == 2

        assert manager_a.ensure_keys() == keys_a
        assert manager_b.ensure_keys() == keys_b
