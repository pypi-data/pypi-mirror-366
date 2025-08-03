"""Test Config.from_env() with unified configuration loading."""

import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import yaml

from flow._internal.config import Config


class TestConfigFromEnv(TestCase):
    """Test Config.from_env() method with various configuration sources."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name) / ".flow"
        self.config_dir.mkdir(exist_ok=True)
        self.config_path = self.config_dir / "config.yaml"

        # Patch the config path
        self.config_path_patch = patch('flow._internal.config_loader.Path.home')
        mock_home = self.config_path_patch.start()
        mock_home.return_value = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test environment."""
        self.config_path_patch.stop()
        self.temp_dir.cleanup()

    def test_from_env_with_env_vars(self):
        """Test loading config from environment variables."""
        with patch.dict(os.environ, {
            'FCP_API_KEY': 'test_api_key',
            'FCP_DEFAULT_PROJECT': 'test-project',
            'FCP_DEFAULT_REGION': 'us-west-1'
        }):
            config = Config.from_env()

            self.assertEqual(config.auth_token, 'test_api_key')
            self.assertEqual(config.provider, 'fcp')
            self.assertEqual(config.provider_config['project'], 'test-project')
            self.assertEqual(config.provider_config['region'], 'us-west-1')

    def test_from_env_with_keychain(self):
        """Test loading config from credentials file."""
        # Write project to config file
        config_data = {'project': 'file-project'}
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Mock credentials file
        with patch('flow._internal.config_loader.ConfigLoader._load_from_credentials_file') as mock_creds:
            mock_creds.return_value = 'creds_api_key'

            config = Config.from_env()

            self.assertEqual(config.auth_token, 'creds_api_key')
            self.assertEqual(config.provider_config['project'], 'file-project')

    def test_from_env_with_config_file(self):
        """Test loading config from config file."""
        # Write complete config
        config_data = {
            'api_key': 'file_api_key',
            'project': 'file-project',
            'region': 'eu-central-1'
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Mock keychain to return None
        with patch('flow._internal.init.writer.ConfigWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer.read_api_key.return_value = None
            mock_writer_class.return_value = mock_writer

            config = Config.from_env()

            self.assertEqual(config.auth_token, 'file_api_key')
            self.assertEqual(config.provider_config['project'], 'file-project')
            self.assertEqual(config.provider_config['region'], 'eu-central-1')

    def test_from_env_no_config_launches_setup(self):
        """Test that missing config raises error when auth required."""
        # Mock keychain to return None
        with patch('flow._internal.init.writer.ConfigWriter') as mock_writer_class:
            mock_writer = MagicMock()
            mock_writer.read_api_key.return_value = None
            mock_writer_class.return_value = mock_writer

            # Should raise error without launching setup
            with self.assertRaises(ValueError) as ctx:
                Config.from_env(require_auth=True)

            self.assertIn("Authentication not configured", str(ctx.exception))

    def test_from_env_with_new_config_format(self):
        """Test loading new provider-based config format."""
        # Write new format config
        config_data = {
            'provider': 'fcp',
            'fcp': {
                'project': 'new-project',
                'region': 'ap-south-1',
                'api_url': 'https://custom.api.com',
                'ssh_keys': ['key1', 'key2']
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        # Set API key in env
        with patch.dict(os.environ, {'FCP_API_KEY': 'env_key'}):
            config = Config.from_env()

            self.assertEqual(config.auth_token, 'env_key')
            self.assertEqual(config.provider_config['project'], 'new-project')
            self.assertEqual(config.provider_config['region'], 'ap-south-1')
            self.assertEqual(config.provider_config['api_url'], 'https://custom.api.com')
            self.assertEqual(config.provider_config['ssh_keys'], ['key1', 'key2'])

    def test_from_env_setup_sets_env_var(self):
        """Test loading config when auth not required."""
        # Save original env
        original_api_key = os.environ.get('FCP_API_KEY')
        try:
            # Clear any existing API key
            os.environ.pop('FCP_API_KEY', None)

            # Mock keychain to return None
            with patch('flow._internal.init.writer.ConfigWriter') as mock_writer_class:
                mock_writer = MagicMock()
                mock_writer.read_api_key.return_value = None
                mock_writer_class.return_value = mock_writer

                # Can load config without auth when not required
                config = Config.from_env(require_auth=False)

                # Should have no auth token
                self.assertIsNone(config.auth_token)
        finally:
            # Restore original env
            if original_api_key is not None:
                os.environ['FCP_API_KEY'] = original_api_key
            else:
                os.environ.pop('FCP_API_KEY', None)

    def test_from_env_placeholder_api_key(self):
        """Test that YOUR_ placeholder API keys are treated as missing."""
        with patch.dict(os.environ, {'FCP_API_KEY': 'YOUR_API_KEY_HERE'}):
            # Should raise error without launching setup
            with self.assertRaises(ValueError) as ctx:
                Config.from_env(require_auth=True)

            self.assertIn("Authentication not configured", str(ctx.exception))
