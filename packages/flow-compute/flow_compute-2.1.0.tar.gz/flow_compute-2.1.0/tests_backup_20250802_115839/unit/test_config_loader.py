"""Test unified configuration loader."""

import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import yaml

from flow._internal.config_loader import ConfigLoader


class TestConfigLoader(TestCase):
    """Test configuration loading from multiple sources."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.yaml"
        self.loader = ConfigLoader(config_path=self.config_path)

    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_precedence_env_over_keychain(self):
        """Test that environment variables take precedence over credentials file."""
        # Set up mock credentials file
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = "creds_api_key"

            # Set environment variable
            with patch.dict(os.environ, {'FCP_API_KEY': 'env_api_key'}):
                sources = self.loader.load_all_sources()

                # Environment should win
                self.assertEqual(sources.api_key, 'env_api_key')

    def test_precedence_keychain_over_file(self):
        """Test that credentials file takes precedence over config file."""
        # Write config file
        config_data = {'api_key': 'file_api_key'}
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Set up mock credentials file
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = "creds_api_key"

            sources = self.loader.load_all_sources()

            # Credentials file should win
            self.assertEqual(sources.api_key, 'creds_api_key')

    def test_fallback_to_config_file(self):
        """Test fallback to config file when no env or credentials file."""
        # Write config file
        config_data = {'api_key': 'file_api_key'}
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Mock credentials file to return None
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None

            sources = self.loader.load_all_sources()

            # File should be used
            self.assertEqual(sources.api_key, 'file_api_key')

    def test_fcp_config_loading(self):
        """Test loading FCP-specific configuration."""
        # Set up config file with new format
        config_data = {
            'provider': 'fcp',
            'fcp': {
                'project': 'my-project',
                'region': 'us-west-2',
                'ssh_keys': ['key1', 'key2']
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        sources = self.loader.load_all_sources()
        fcp_config = sources.get_fcp_config()

        self.assertEqual(fcp_config['project'], 'my-project')
        self.assertEqual(fcp_config['region'], 'us-west-2')
        self.assertEqual(fcp_config['ssh_keys'], ['key1', 'key2'])

    def test_legacy_config_format(self):
        """Test loading legacy flat config format."""
        # Write legacy format config
        config_data = {
            'api_key': 'legacy_key',
            'project': 'legacy-project',
            'region': 'legacy-region',
            'default_ssh_key': 'legacy_ssh_key'
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Mock credentials file to return None so config file is used
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None
            
            sources = self.loader.load_all_sources()
            fcp_config = sources.get_fcp_config()

            self.assertEqual(sources.api_key, 'legacy_key')
            self.assertEqual(fcp_config['project'], 'legacy-project')
            self.assertEqual(fcp_config['region'], 'legacy-region')
            self.assertEqual(fcp_config['ssh_keys'], ['legacy_ssh_key'])

    def test_env_vars_override_file(self):
        """Test that environment variables override file values."""
        # Write config file
        config_data = {
            'fcp': {
                'project': 'file-project',
                'region': 'file-region'
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Set environment variables
        with patch.dict(os.environ, {
            'FCP_DEFAULT_PROJECT': 'env-project',
            'FCP_DEFAULT_REGION': 'env-region'
        }):
            sources = self.loader.load_all_sources()
            fcp_config = sources.get_fcp_config()

            # Environment should win
            self.assertEqual(fcp_config['project'], 'env-project')
            self.assertEqual(fcp_config['region'], 'env-region')

    def test_has_valid_config(self):
        """Test configuration validation."""
        # Mock credentials file to return None
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None
            
            # No config
            self.assertFalse(self.loader.has_valid_config())

            # YOUR_ placeholder
            with patch.dict(os.environ, {'FCP_API_KEY': 'YOUR_API_KEY'}, clear=True):
                self.assertFalse(self.loader.has_valid_config())

            # Valid config
            with patch.dict(os.environ, {'FCP_API_KEY': 'valid_key'}, clear=True):
                self.assertTrue(self.loader.has_valid_config())

    def test_missing_config_file(self):
        """Test behavior when config file doesn't exist."""
        # Ensure file doesn't exist
        if self.config_path.exists():
            self.config_path.unlink()

        # Mock credentials file to return None
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None
            
            sources = self.loader.load_all_sources()

            # Should return empty config
            self.assertEqual(sources.config_file, {})
            self.assertIsNone(sources.api_key)

    def test_invalid_yaml_file(self):
        """Test behavior with invalid YAML in config file."""
        # Write invalid YAML
        with open(self.config_path, 'w') as f:
            f.write("invalid: yaml: content: [")

        # Should raise ConfigParserError with helpful suggestions
        from flow.errors import ConfigParserError
        with self.assertRaises(ConfigParserError) as cm:
            self.loader.load_all_sources()

        # Verify error has proper structure
        self.assertIn("Invalid YAML syntax", str(cm.exception))
        self.assertEqual(cm.exception.error_code, "CONFIG_001")

    def test_keychain_error_handling(self):
        """Test that credentials file errors are handled gracefully."""
        # Mock the method to return None (simulating graceful error handling)
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = None

            sources = self.loader.load_all_sources()

            # Should continue without credentials
            self.assertIsNone(sources.keychain_api_key)
