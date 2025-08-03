"""Unit tests for ConfigWriter."""

import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import yaml

from flow._internal.init.writer import ConfigWriter
from flow.api.models import ValidationResult


class TestConfigWriter(TestCase):
    """Test configuration persistence."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"
        self.writer = ConfigWriter(
            config_path=self.config_path
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_config_and_credentials(self):
        """Test writing config to file and API key to credentials file."""
        config = {
            "api_key": "secret_key",
            "provider": "fcp",
            "project": "test_project",
            "region": "us-central1-a",
            "api_url": "https://api.test.com"
        }
        validation = ValidationResult(is_valid=True, projects=[])

        self.writer.write(config, validation)

        # Check credentials file was written
        credentials_path = Path(self.temp_dir) / "credentials.fcp"
        self.assertTrue(credentials_path.exists())
        
        # Check API key was stored
        stored_key = self.writer.read_api_key("fcp")
        self.assertEqual(stored_key, "secret_key")

        # Check config file was written (without api_key)
        self.assertTrue(self.config_path.exists())
        with open(self.config_path) as f:
            saved_config = yaml.safe_load(f)

        self.assertNotIn("api_key", saved_config)
        self.assertEqual(saved_config["provider"], "fcp")
        self.assertEqual(saved_config["fcp"]["project"], "test_project")
        self.assertEqual(saved_config["fcp"]["region"], "us-central1-a")
        self.assertEqual(saved_config["fcp"]["api_url"], "https://api.test.com")

        # Check file permissions (Unix only)
        if os.name != 'nt':
            stat_info = self.config_path.stat()
            self.assertEqual(stat_info.st_mode & 0o777, 0o600)

    def test_write_no_api_key(self):
        """Test writing config without API key."""
        config = {
            "provider": "fcp",
            "project": "test_project",
            "region": "us-central1-a"
        }
        validation = ValidationResult(is_valid=True, projects=[])

        self.writer.write(config, validation)

        # Credentials file should not be written
        credentials_path = Path(self.temp_dir) / "credentials.fcp"
        self.assertFalse(credentials_path.exists())

        # Config file should be written
        self.assertTrue(self.config_path.exists())
        with open(self.config_path) as f:
            saved_config = yaml.safe_load(f)

        self.assertEqual(saved_config["provider"], "fcp")
        self.assertEqual(saved_config["fcp"]["project"], "test_project")
        self.assertEqual(saved_config["fcp"]["region"], "us-central1-a")

    def test_credentials_file_write_failure(self):
        """Test that credentials file write failure doesn't prevent config write."""
        config = {
            "api_key": "secret_key",
            "provider": "fcp",
            "project": "test_project"
        }
        validation = ValidationResult(is_valid=True, projects=[])

        # Mock credentials write failure
        with patch.object(self.writer, '_write_provider_credentials', side_effect=Exception("Write error")):
            # Should raise the exception
            with self.assertRaises(Exception):
                self.writer.write(config, validation)

        # Config file should still be written
        self.assertTrue(self.config_path.exists())
        with open(self.config_path) as f:
            saved_config = yaml.safe_load(f)

        self.assertEqual(saved_config["provider"], "fcp")
        self.assertEqual(saved_config["fcp"]["project"], "test_project")

    def test_read_api_key(self):
        """Test reading API key from credentials file."""
        # First write an API key
        config = {
            "api_key": "stored_key",
            "provider": "fcp"
        }
        validation = ValidationResult(is_valid=True, projects=[])
        self.writer.write(config, validation)

        # Now read it back
        key = self.writer.read_api_key("fcp")
        self.assertEqual(key, "stored_key")

    def test_read_api_key_not_found(self):
        """Test reading API key when credentials file doesn't exist."""
        key = self.writer.read_api_key("fcp")
        self.assertIsNone(key)

    def test_read_api_key_error(self):
        """Test reading API key when credentials file is malformed."""
        # Write a malformed credentials file
        credentials_path = Path(self.temp_dir) / "credentials.fcp"
        credentials_path.write_text("malformed content")

        key = self.writer.read_api_key("fcp")
        self.assertIsNone(key)

    def test_atomic_write(self):
        """Test atomic file writing."""
        # Write initial config
        config1 = {"provider": "fcp", "project": "project1", "region": "us-central1-a"}
        validation = ValidationResult(is_valid=True, projects=[])
        self.writer.write(config1, validation)

        # Simulate write failure during second write
        config2 = {"provider": "fcp", "project": "project2", "region": "eu-west1"}

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            # Make temp file creation fail after write
            mock_file = MagicMock()
            mock_temp.return_value.__enter__.return_value = mock_file
            mock_file.name = "/nonexistent/path"

            try:
                self.writer.write(config2, validation)
            except:
                pass

        # Original config should still be intact
        with open(self.config_path) as f:
            saved_config = yaml.safe_load(f)

        self.assertEqual(saved_config["provider"], "fcp")
        self.assertEqual(saved_config["fcp"]["project"], "project1")

    def test_creates_parent_directory(self):
        """Test that parent directory is created if missing."""
        nested_path = Path(self.temp_dir) / "nested" / "dir" / "config.yaml"
        writer = ConfigWriter(
            config_path=nested_path
        )

        config = {"provider": "fcp", "project": "test"}
        validation = ValidationResult(is_valid=True, projects=[])

        writer.write(config, validation)

        self.assertTrue(nested_path.exists())
        self.assertTrue(nested_path.parent.exists())
