"""Test flow init reconfiguration behavior."""

import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import yaml
from click.testing import CliRunner

from flow.cli.app import cli


class TestFlowInitReconfigure(TestCase):
    """Test flow init with existing configuration."""

    def setUp(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.old_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir

        # Clear any existing env vars
        for key in ['FCP_API_KEY', 'FCP_PROJECT', 'FCP_REGION', 'FCP_API_URL']:
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
    @patch('flow.cli.commands.init.HttpClient')
    @patch('keyring.get_keyring')
    def test_init_with_valid_config_no_reconfigure(self, mock_keyring_func, mock_http_client, mock_flow):
        """Test init with valid config - user chooses not to reconfigure."""
        # Set up existing config
        config_dir = Path(self.temp_dir) / '.flow'
        config_dir.mkdir()
        config_path = config_dir / 'config.yaml'

        with open(config_path, 'w') as f:
            yaml.dump({
                'provider': 'fcp',
                'api_key': 'existing_api_key',
                'project': 'existing-project',
                'region': 'us-central1-a',
                'api_url': 'https://api.mlfoundry.com'
            }, f)

        # Mock keyring
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Mock HTTP client
        mock_client_instance = MagicMock()
        mock_http_client.return_value = mock_client_instance

        # Mock successful API validation
        mock_client_instance.request.return_value = []  # Empty projects list

        # Mock Flow client for final verification
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_flow_instance.list_tasks.return_value = []  # Empty tasks list

        # Run init and choose to verify and exit (option 2)
        result = self.runner.invoke(cli, ['init'], input='2\n')

        # Check output
        self.assertEqual(result.exit_code, 0)
        self.assertIn('All required components are configured', result.output)
        self.assertIn('Verify configuration and exit', result.output)
        self.assertIn('Configuration verified successfully', result.output)

        # Config should remain unchanged
        with open(config_path) as f:
            config = yaml.safe_load(f)
        self.assertEqual(config['project'], 'existing-project')

    @patch('flow.cli.commands.init.Flow')
    @patch('flow.cli.commands.init.HttpClient')
    @patch('keyring.get_keyring')
    def test_init_with_valid_config_reconfigure(self, mock_keyring_func, mock_http_client, mock_flow):
        """Test init with valid config - user chooses to reconfigure."""
        # Set up existing config
        config_dir = Path(self.temp_dir) / '.flow'
        config_dir.mkdir()
        config_path = config_dir / 'config.yaml'

        with open(config_path, 'w') as f:
            yaml.dump({
                'provider': 'fcp',
                'api_key': 'existing_api_key',
                'project': 'old-project',
                'region': 'us-central1-a',
                'api_url': 'https://api.mlfoundry.com'
            }, f)

        # Mock keyring
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Mock HTTP client
        mock_client_instance = MagicMock()
        mock_http_client.return_value = mock_client_instance

        # Mock API responses
        mock_client_instance.request.side_effect = [
            # First validation (existing config)
            [],  # Empty projects list
            # When reconfiguring project
            [{"name": "project1", "region": "us-central1-a"},
             {"name": "project2", "region": "eu-west1"}]
        ]

        # Mock Flow client for final verification
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_flow_instance.list_tasks.return_value = []  # Empty tasks list

        # Run init and choose to reconfigure
        # 1. Choose option 3 (Reconfigure components)
        # 2. Option 2 (Configure Project)
        # 3. Select project 1
        # 4. Option 0 (Done - save and exit)
        # 5. Don't create example file
        result = self.runner.invoke(
            cli,
            ['init'],
            input='3\n2\n1\n0\nn\n'
        )

        # Check output
        self.assertEqual(result.exit_code, 0)
        self.assertIn('All required components are configured', result.output)
        self.assertIn('Reconfigure components', result.output)
        self.assertIn('Configuration saved to:', result.output)

        # Config should be updated
        with open(config_path) as f:
            config = yaml.safe_load(f)
        # Config is now in nested format under provider key
        self.assertIn('fcp', config)
        self.assertIn('project', config['fcp'])
        # Project should be saved as '1' (user input)
        self.assertEqual(config['fcp']['project'], '1')

    @patch('keyring.get_keyring')
    def test_init_with_missing_config_proceeds_normally(self, mock_keyring_func):
        """Test init with no existing config proceeds with normal flow."""
        # Mock keyring with no stored key
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Run init in non-interactive mode - no existing config
        result = self.runner.invoke(
            cli,
            ['init',
             '--provider', 'fcp',
             '--api-key', 'fkey_test123',
             '--project', 'my_project',
             '--region', 'us-central1-a'
            ]
        )

        # Should go through full setup
        self.assertEqual(result.exit_code, 0)
        # Non-interactive mode doesn't show the wizard welcome screen
        self.assertIn('Configuration saved', result.output)
        # It should not show the 'all configured' message since this is a fresh install
        self.assertNotIn('All required components are configured', result.output)

    @patch('flow.cli.commands.init.Flow')
    @patch('flow.cli.commands.init.HttpClient')
    @patch('keyring.get_keyring')
    def test_init_with_cli_args_skips_prompt(self, mock_keyring_func, mock_http_client, mock_flow):
        """Test init with CLI arguments skips reconfigure prompt."""
        # Set up existing config
        config_dir = Path(self.temp_dir) / '.flow'
        config_dir.mkdir()
        config_path = config_dir / 'config.yaml'

        with open(config_path, 'w') as f:
            yaml.dump({
                'provider': 'fcp',
                'api_key': 'old_api_key',
                'project': 'old-project',
                'region': 'us-central1-a',
                'api_url': 'https://api.mlfoundry.com'
            }, f)

        # Mock keyring
        mock_keyring = MagicMock()
        mock_keyring_func.return_value = mock_keyring
        mock_keyring.get_password.return_value = None

        # Mock HTTP client
        mock_client_instance = MagicMock()
        mock_http_client.return_value = mock_client_instance

        # Mock successful API validation
        mock_client_instance.request.return_value = []  # Empty projects list

        # Mock Flow client for final verification
        mock_flow_instance = MagicMock()
        mock_flow.return_value = mock_flow_instance
        mock_flow_instance.list_tasks.return_value = []  # Empty tasks list

        # Run init with new project - provide all values to avoid prompts
        result = self.runner.invoke(
            cli,
            ['init', '--provider', 'fcp', '--api-key', 'existing_api_key', '--project', 'new-project', '--region', 'us-central1-a']
        )

        # Should not ask about reconfiguring
        if result.exit_code != 0:
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.output}")
            print(f"Exception: {result.exception}")
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn('All required components are configured', result.output)
        self.assertIn('Configuration saved', result.output)

        # Config should be updated
        with open(config_path) as f:
            config = yaml.safe_load(f)
        self.assertEqual(config['project'], 'new-project')
