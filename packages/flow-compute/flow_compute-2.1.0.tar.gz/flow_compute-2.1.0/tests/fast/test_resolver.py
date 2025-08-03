"""Unit tests for ConfigResolver."""

import tempfile
from pathlib import Path
from unittest import TestCase

import yaml

from flow._internal.init.resolver import ConfigResolver


class TestConfigResolver(TestCase):
    """Test configuration resolution from multiple sources."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"
        self.resolver = ConfigResolver(config_path=self.config_path)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_resolve_defaults_only(self):
        """Test resolution with no inputs returns defaults."""
        config = self.resolver.resolve(cli_args={}, env={})

        self.assertIsNone(config["api_key"])
        self.assertIsNone(config["project"])
        self.assertEqual(config["region"], "us-central1-a")
        self.assertEqual(config["api_url"], "https://api.mlfoundry.com")

    def test_resolve_from_file(self):
        """Test resolution from config file."""
        # Write test config
        test_config = {
            "api_key": "file_key",
            "project": "file_project",
            "region": "eu-west1"
        }
        with open(self.config_path, "w") as f:
            yaml.dump(test_config, f)

        config = self.resolver.resolve(cli_args={}, env={})

        self.assertEqual(config["api_key"], "file_key")
        self.assertEqual(config["project"], "file_project")
        self.assertEqual(config["region"], "eu-west1")

    def test_resolve_from_env(self):
        """Test resolution from environment variables."""
        env = {
            "FCP_API_KEY": "env_key",
            "FCP_PROJECT": "env_project",
            "FCP_REGION": "us-west2",
            "FCP_API_URL": "https://custom.api.com"
        }

        config = self.resolver.resolve(cli_args={}, env=env)

        self.assertEqual(config["api_key"], "env_key")
        self.assertEqual(config["project"], "env_project")
        self.assertEqual(config["region"], "us-west2")
        self.assertEqual(config["api_url"], "https://custom.api.com")

    def test_resolve_from_cli(self):
        """Test resolution from CLI arguments."""
        cli_args = {
            "api_key": "cli_key",
            "project": "cli_project",
            "region": "asia-east1",
            "api_url": None  # Should not override
        }

        config = self.resolver.resolve(cli_args=cli_args, env={})

        self.assertEqual(config["api_key"], "cli_key")
        self.assertEqual(config["project"], "cli_project")
        self.assertEqual(config["region"], "asia-east1")
        self.assertEqual(config["api_url"], "https://api.mlfoundry.com")  # Default

    def test_precedence_order(self):
        """Test CLI > ENV > file precedence."""
        # Write file config
        with open(self.config_path, "w") as f:
            yaml.dump({
                "api_key": "file_key",
                "project": "file_project",
                "region": "file_region"
            }, f)

        # Set env vars
        env = {
            "FCP_API_KEY": "env_key",
            "FCP_PROJECT": "env_project"
        }

        # Set CLI args
        cli_args = {
            "api_key": "cli_key"
        }

        config = self.resolver.resolve(cli_args=cli_args, env=env)

        # CLI wins for api_key
        self.assertEqual(config["api_key"], "cli_key")
        # ENV wins for project (no CLI value)
        self.assertEqual(config["project"], "env_project")
        # File wins for region (no CLI or ENV value)
        self.assertEqual(config["region"], "file_region")

    def test_corrupted_config_file(self):
        """Test graceful handling of corrupted config file."""
        # Write invalid YAML
        with open(self.config_path, "w") as f:
            f.write("invalid: yaml: content: [")

        # Should not raise, should use other sources
        config = self.resolver.resolve(
            cli_args={"project": "cli_project"},
            env={}
        )

        self.assertEqual(config["project"], "cli_project")
        self.assertIsNone(config["api_key"])

    def test_get_missing_required_fields(self):
        """Test identification of missing required fields."""
        # All missing
        config = {"api_key": None, "project": None}
        missing = self.resolver.get_missing_required_fields(config)
        self.assertEqual(set(missing), {"api_key", "project"})

        # API key present
        config = {"api_key": "key", "project": None}
        missing = self.resolver.get_missing_required_fields(config)
        self.assertEqual(missing, ["project"])

        # All present
        config = {"api_key": "key", "project": "proj"}
        missing = self.resolver.get_missing_required_fields(config)
        self.assertEqual(missing, [])
