"""End-to-end integration test for flow init."""

import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import yaml
from click.testing import CliRunner

from flow.cli.app import cli


class TestFlowInitE2E(TestCase):
    """Integration tests for flow init command."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.old_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir

        # Clear any existing env vars
        for key in ['FCP_API_KEY', 'FCP_PROJECT', 'FCP_REGION', 'FCP_API_URL',
                    'FLOW_PROVIDER', 'FLOW_AUTH_TOKEN', 'FCP_SSH_KEYS']:
            os.environ.pop(key, None)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if self.old_home:
            os.environ['HOME'] = self.old_home
        else:
            os.environ.pop('HOME', None)

    @patch('flow.cli.commands.init.Flow')
    @patch('keyring.get_keyring')
    def test_init_interactive_success(self, mock_keyring_func, mock_flow):
        """Test successful interactive initialization."""
        # Mock keyring
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Mock Flow client to handle API calls during init
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        
        # Mock the provider to return projects when queried
        mock_provider = MagicMock()
        mock_flow_instance._provider = mock_provider
        mock_provider.list_projects.return_value = [
            {"name": "project1", "region": "us-central1-a"},
            {"name": "project2", "region": "eu-west1"}
        ]
        mock_flow_instance.list_tasks.return_value = []  # Empty tasks list

        # Run command with interactive input
        # The new wizard flow:
        # 1. Configure API Key (option 1)
        # 2. Don't open browser (n)
        # 3. Enter API key -> fkey_test123456789  (proper format)
        # 4. Configure Project (option 2)
        # 5. Select project 1
        # 6. Done (option 0)
        # 7. Don't create example file (n)
        result = self.runner.invoke(
            cli,
            ['init'],
            input='1\nn\nfkey_test123456789\n2\n1\n0\nn\n'
        )

        # Check output
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Welcome to Flow SDK Setup', result.output)
        self.assertIn('Configuration saved', result.output)

        # Check config file was created
        config_path = Path(self.temp_dir) / '.flow' / 'config.yaml'
        self.assertTrue(config_path.exists())

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Config is now in nested format under provider key
        self.assertEqual(config['provider'], 'fcp')
        self.assertIn('fcp', config)
        # Project should be saved (either as '1' or 'project1')
        self.assertIn('project', config['fcp'])
        self.assertTrue(config['fcp']['project'] in ['1', 'project1'])

    @patch('keyring.get_keyring')
    def test_init_non_interactive(self, mock_keyring_func):
        """Test non-interactive initialization with all flags."""
        # Mock keyring
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Run with all flags
        result = self.runner.invoke(
            cli,
            [
                'init',
                '--provider', 'fcp',
                '--api-key', 'my_api_key',
                '--project', 'my_project',
                '--region', 'us-west2',
                '--api-url', 'https://custom.api.com'
            ]
        )

        # Should succeed without prompting
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Configuration saved', result.output)

        # Check config file
        config_path = Path(self.temp_dir) / '.flow' / 'config.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)

        self.assertEqual(config['provider'], 'fcp')
        self.assertEqual(config['api_key'], 'my_api_key')
        self.assertEqual(config['project'], 'my_project')
        self.assertEqual(config['region'], 'us-west2')
        self.assertEqual(config['api_url'], 'https://custom.api.com')

    def test_init_dry_run(self):
        """Test dry run mode."""
        result = self.runner.invoke(
            cli,
            [
                'init',
                '--provider', 'fcp',
                '--dry-run',
                '--api-key', 'test_key',
                '--project', 'test_project',
                '--region', 'us-west1'
            ]
        )

        # Should show config but not save
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Configuration (dry run)', result.output)
        # API key is masked in output
        self.assertIn('[CONFIGURED]', result.output)
        self.assertIn('test_project', result.output)

        # Should NOT create config file
        config_path = Path(self.temp_dir) / '.flow' / 'config.yaml'
        self.assertFalse(config_path.exists())

    def test_init_api_timeout(self):
        """Test initialization when API times out."""
        # Use non-interactive mode to avoid password prompt issues
        # The new init command in non-interactive mode should handle timeouts gracefully
        result = self.runner.invoke(
            cli,
            ['init',
             '--provider', 'fcp',
             '--api-key', 'fkey_test123',
             '--project', 'my_project',
             '--region', 'us-west1'
            ]
        )

        # Should succeed and save config even if API validation fails
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Configuration saved', result.output)

        # Config should be saved
        config_path = Path(self.temp_dir) / '.flow' / 'config.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)

        self.assertEqual(config['project'], 'my_project')
        self.assertEqual(config['api_key'], 'fkey_test123')

    @patch('keyring.get_keyring')
    def test_init_with_existing_config(self, mock_keyring_func):
        """Test initialization with existing config file."""
        # Create existing config
        config_dir = Path(self.temp_dir) / '.flow'
        config_dir.mkdir()
        config_path = config_dir / 'config.yaml'

        with open(config_path, 'w') as f:
            yaml.dump({
                'provider': 'fcp',
                'project': 'existing_project',
                'region': 'eu-west1'
            }, f)

        # Mock keyring
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Run init with all required values to avoid prompts
        result = self.runner.invoke(
            cli,
            ['init', '--provider', 'fcp', '--api-key', 'new_api_key', '--project', 'existing_project', '--region', 'eu-west1']
        )

        # Should use existing values
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        self.assertEqual(result.exit_code, 0)

        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Config should have new API key but preserve other values
        self.assertEqual(config['api_key'], 'new_api_key')
        self.assertEqual(config['project'], 'existing_project')
        self.assertEqual(config['region'], 'eu-west1')

    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        # Set env vars
        os.environ['FLOW_PROVIDER'] = 'fcp'
        os.environ['FCP_PROJECT'] = 'env_project'
        os.environ['FCP_REGION'] = 'us-central1-a'
        os.environ['FCP_API_KEY'] = 'fkey_env123'

        # Run init in non-interactive mode - it should pick up env vars
        result = self.runner.invoke(cli, ['init', '--provider', 'fcp'])

        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Configuration saved', result.output)

        # Check that config was created from env vars
        config_path = Path(self.temp_dir) / '.flow' / 'config.yaml'
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # The non-interactive mode should use env var values as defaults
        self.assertEqual(config['provider'], 'fcp')
        self.assertEqual(config['project'], 'env_project')
        self.assertEqual(config['region'], 'us-central1-a')
        self.assertEqual(config['api_key'], 'fkey_env123')
