"""Init command for Flow SDK configuration.

Supports both interactive wizard and direct configuration via flags.

Examples:
    Interactive setup:
        $ flow init

    Direct configuration:
        $ flow init --provider fcp --api-key fkey_xxx --project myproject

    Dry run to preview:
        $ flow init --provider fcp --dry-run
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

import click
import yaml
from flow.cli.commands.base import BaseCommand
from ..utils.theme_manager import theme_manager
from flow.cli.utils.config_validator import ConfigValidator, ValidationStatus
from flow.cli.provider_resolver import ProviderResolver

# Import private components
from flow.core.setup_registry import SetupRegistry, register_providers

logger = logging.getLogger(__name__)

# Create console instance
console = theme_manager.create_console()


def run_setup_wizard():
    """Entry point for the Flow SDK setup wizard.

    Returns:
        bool: True if setup completed successfully, False otherwise

    This function:
    - Creates and runs the generic setup wizard with registered adapter
    - Handles keyboard interrupts gracefully
    - Logs any unexpected errors for debugging

    Example:
        >>> from flow.cli.commands.init import run_setup_wizard
        >>> if run_setup_wizard():
        ...     print("Setup successful!")
        ... else:
        ...     print("Setup failed or was cancelled")
    """
    from flow.core.generic_setup_wizard import GenericSetupWizard

    # Register providers first
    register_providers()

    # Get FCP adapter from registry (proper abstraction)
    adapter = SetupRegistry.get_adapter("fcp")
    if not adapter:
        console.print("[red]Error: FCP provider not available[/red]")
        return False

    wizard = GenericSetupWizard(console, adapter)

    try:
        return wizard.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup cancelled[/yellow]")
        return False
    except Exception as e:
        console.print(f"\n\n[red]Setup error:[/red] {e}")
        logger.exception("Setup wizard error")
        return False


class InitCommand(BaseCommand):
    """Init command implementation.

    Handles both interactive wizard mode and direct configuration
    via command-line options.
    """

    def __init__(self):
        """Initialize init command."""
        super().__init__()
        self.validator = ConfigValidator()

    @property
    def name(self) -> str:
        return "init"

    @property
    def help(self) -> str:
        return "Configure Flow SDK credentials and provider settings"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--provider", envvar="FLOW_PROVIDER", help="Provider to use")
        @click.option("--api-key", help="API key for authentication")
        @click.option("--project", help="Project name")
        @click.option("--region", help="Default region")
        @click.option("--api-url", help="API endpoint URL")
        @click.option("--dry-run", is_flag=True, help="Show configuration without saving")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed setup information")
        def init(
            provider: Optional[str],
            api_key: Optional[str],
            project: Optional[str],
            region: Optional[str],
            api_url: Optional[str],
            dry_run: bool,
            verbose: bool,
        ):
            """Configure Flow SDK.

            \b
            Examples:
                flow init                    # Interactive setup wizard
                flow init --dry-run          # Preview configuration
                flow init --provider fcp --api-key xxx  # Direct setup

            Use 'flow init --verbose' for detailed configuration options.
            """
            if verbose and not any([provider, api_key, project, region, api_url, dry_run]):
                console.print("\n[bold]Flow SDK Configuration Guide:[/bold]\n")
                console.print("Interactive setup:")
                console.print("  flow init                         # Step-by-step wizard")
                console.print("  flow init --dry-run               # Preview without saving\n")
                
                console.print("Direct configuration:")
                console.print("  flow init --provider fcp --api-key fkey_xxx --project myproject")
                console.print("  flow init --region us-west-2      # Set default region")
                console.print("  flow init --api-url https://custom.api.com  # Custom endpoint\n")
                
                console.print("Environment variables:")
                console.print("  export FLOW_API_KEY=fkey_xxx      # Set API key")
                console.print("  export FLOW_PROJECT=myproject     # Set project")
                console.print("  export FLOW_REGION=us-west-2      # Set region\n")
                
                console.print("Configuration files:")
                console.print("  ~/.flow/config.yaml               # User configuration")
                console.print("  ./.flow/config.yaml               # Project configuration")
                console.print("  $FLOW_CONFIG                      # Custom config path\n")
                
                console.print("Next steps after init:")
                console.print("  • Test connection: flow health")
                console.print("  • Upload SSH keys: flow ssh-keys upload ~/.ssh/id_rsa.pub")
                console.print("  • Run first task: flow run examples/hello-gpu.yaml")
                console.print("  • Start dev environment: flow dev\n")
                return
                
            # Run async function
            asyncio.run(self._init_async(provider, api_key, project, region, api_url, dry_run, verbose))

        return init

    async def _init_async(
        self,
        provider: Optional[str],
        api_key: Optional[str],
        project: Optional[str],
        region: Optional[str],
        api_url: Optional[str],
        dry_run: bool,
        verbose: bool = False,
    ):
        """Execute init command.

        Args:
            provider: Provider name
            api_key: API key for authentication
            project: Project name
            region: Default region
            api_url: Custom API endpoint
            dry_run: Preview without saving
        """
        if provider or api_key or project or region or api_url or dry_run:
            # Non-interactive mode with provided options
            await self._configure_with_options(provider, api_key, project, region, api_url, dry_run)
        else:
            # Interactive mode - use refactored wizard
            success = run_setup_wizard()
            if success:
                # Show next actions after successful setup
                console.print("")  # Add blank line for spacing
                self.show_next_actions(
                    [
                        "Run an example: [cyan]flow example minimal[/cyan]",
                        "View all examples: [cyan]flow example[/cyan]",
                        "Submit your first task: [cyan]flow run task.yaml[/cyan]",
                    ]
                )
            else:
                raise click.exceptions.Exit(1)

    async def _configure_with_options(
        self,
        provider: Optional[str],
        api_key: Optional[str],
        project: Optional[str],
        region: Optional[str],
        api_url: Optional[str],
        dry_run: bool,
    ):
        """Configure using command-line options.

        Prompts for missing required values if needed.
        Validates provider and saves configuration.
        """
        # Require provider to be specified
        if not provider:
            console.print("[red]Error:[/red] Provider must be specified with --provider")
            raise click.exceptions.Exit(1)

        # Register providers
        register_providers()

        # Try new provider-based setup first
        setup = SetupRegistry.get_setup(provider)
        if setup:
            # Use new architecture
            result = setup.setup_with_options(
                api_key=api_key, project=project, region=region, api_url=api_url
            )

            if result.success:
                if not dry_run:
                    # Save configuration
                    config = {"provider": provider}
                    config.update(result.config)

                    config_dir = Path.home() / ".flow"
                    config_dir.mkdir(exist_ok=True)
                    config_path = config_dir / "config.yaml"

                    with open(config_path, "w") as f:
                        yaml.safe_dump(config, f, default_flow_style=False)

                    console.print(f"\n[green]✓[/green] Configuration saved to {config_path}")
                    console.print("\n[yellow]ℹ SSH Keys:[/yellow]")
                    console.print("  Flow automatically generates FCP-specific SSH keys for secure instance access.")
                    
                    self.show_next_actions(
                        [
                            "Test your setup: [cyan]flow health[/cyan]",
                            "Run an example: [cyan]flow example minimal[/cyan]",
                            "View all examples: [cyan]flow example[/cyan]",
                            "Submit your first task: [cyan]flow run task.yaml[/cyan]",
                            "(Optional) Upload existing SSH key: [cyan]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/cyan]",
                        ]
                    )
                else:
                    console.print("\n[dim]Dry run - configuration not saved[/dim]")
                    console.print(yaml.safe_dump(result.config, default_flow_style=False))
            else:
                console.print(f"[red]Configuration failed:[/red] {result.message}")
                raise click.exceptions.Exit(1)
            return

        # Fall back to old implementation for backward compatibility
        # Get provider manifest
        try:
            manifest = ProviderResolver.get_manifest(provider)
        except Exception:
            console.print(f"[red]Error:[/red] Unknown provider: {provider}")
            raise click.exceptions.Exit(1)

        # Build configuration
        config = {"provider": provider}

        # Get environment variable mappings
        env_vars = ProviderResolver.get_env_vars(provider)

        # Process provider-specific configuration fields
        if api_key:
            # Validate API key format using provider rules
            if ProviderResolver.validate_config_value(provider, "api_key", api_key):
                config["api_key"] = api_key
            else:
                console.print(f"[yellow]Warning: Invalid API key format for {provider}[/yellow]")
                config["api_key"] = api_key
        else:
            # Try to get from environment or interactive input
            env_var = env_vars.get("api_key")
            default_value = os.environ.get(env_var) if env_var else None
            api_key = await self._prompt_for_value("API Key", password=True, default=default_value)
            if api_key:
                # Show masked feedback
                masked_key = f"{api_key[:5]}{'*' * (len(api_key) - 9)}{api_key[-4:]}"
                console.print(f"[dim]Received: {masked_key}[/dim]")
                config["api_key"] = api_key

        if project:
            # Validate project name using provider rules
            if ProviderResolver.validate_config_value(provider, "project", project):
                config["project"] = project
            else:
                console.print(
                    f"[yellow]Warning: Invalid project name format for {provider}[/yellow]"
                )
                config["project"] = project
        else:
            env_var = env_vars.get("project")
            default_value = os.environ.get(env_var, "default") if env_var else "default"
            project = await self._prompt_for_value("Project", default=default_value)
            if project:
                config["project"] = project

        if region:
            # Validate region using provider rules
            if ProviderResolver.validate_config_value(provider, "region", region):
                config["region"] = region
            else:
                console.print(f"[yellow]Warning: Invalid region format for {provider}[/yellow]")
                config["region"] = region
        else:
            env_var = env_vars.get("region")
            default_region = ProviderResolver.get_default_region(provider)
            default_value = os.environ.get(env_var, default_region) if env_var else default_region
            region = await self._prompt_for_value("Region", default=default_value)
            if region:
                config["region"] = region

        if api_url:
            config["api_url"] = api_url

        if dry_run:
            # Show configuration without saving
            console.print("\n[bold]Configuration (dry run)[/bold]")
            console.print("─" * 50)
            console.print(f"Provider: {provider}")

            # Display all configuration fields
            for key, value in config.items():
                if key == "provider":
                    continue
                if key == "api_key":
                    masked_key = self._mask_api_key(value)
                    console.print(f"API Key: {masked_key}")
                else:
                    console.print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            # Save configuration
            config_path = Path.home() / ".flow" / "config.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            import yaml

            with open(config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

            config_path.chmod(0o600)
            console.print(f"[green]✓[/green] Configuration saved to: {config_path}")
            
            console.print("\n[yellow]ℹ SSH Keys:[/yellow]")
            console.print("  Flow automatically generates FCP-specific SSH keys for secure instance access.")
            
            self.show_next_actions(
                [
                    "Test your setup: [cyan]flow health[/cyan]",
                    "Run an example: [cyan]flow example minimal[/cyan]",
                    "View all examples: [cyan]flow example[/cyan]",
                    "Submit your first task: [cyan]flow run task.yaml[/cyan]",
                    "(Optional) Upload existing SSH key: [cyan]flow ssh-keys upload ~/.ssh/id_ed25519.pub[/cyan]",
                ]
            )

    async def _prompt_for_value(
        self, name: str, password: bool = False, default: Optional[str] = None
    ) -> Optional[str]:
        """Prompt user for configuration value.

        Args:
            name: Value name to prompt for
            password: Hide input for sensitive values
            default: Default value if none provided

        Returns:
            User input or None
        """
        from rich.prompt import Prompt

        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: Prompt.ask(name, password=password, default=default)
        )

    def _mask_api_key(self, api_key: str) -> str:
        """Mask API key for safe display.

        Example:
            'fkey_abcd1234efgh5678' -> 'fkey_abc...5678'
        """
        if len(api_key) > 10:
            return f"{api_key[:8]}...{api_key[-4:]}"
        return "[CONFIGURED]"


# Export command instance
command = InitCommand()
