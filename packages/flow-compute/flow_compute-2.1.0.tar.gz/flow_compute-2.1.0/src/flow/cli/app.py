"""Flow CLI application module.

This module provides the main CLI entry point and command registration
for the Flow GPU task orchestration system.
"""

import os
import sys

import click

from flow import Flow  # noqa: F401
from flow.cli.commands import get_commands


@click.group()
@click.version_option(version="2.0.0", prog_name="flow")
@click.option("--theme", envvar="FLOW_THEME", help="Set color theme (dark, light, high_contrast)")
@click.option("--no-color", envvar="NO_COLOR", is_flag=True, help="Disable color output")
@click.option(
    "--hyperlinks/--no-hyperlinks",
    envvar="FLOW_HYPERLINKS",
    default=None,
    help="Enable/disable hyperlinks",
)
@click.pass_context
def cli(ctx, theme, no_color, hyperlinks):
    """Flow CLI - Submit and manage GPU tasks.

    This is the main command group for the Flow CLI. It provides
    commands for submitting, monitoring, and managing GPU compute tasks.

    Examples:
        First-time setup:
            $ flow init

        Start a cloud dev environment:
            $ flow dev

        Test GPU access:
            $ flow example gpu-test

        Check your running tasks:
            $ flow status

        SSH into a running task:
            $ flow ssh task_123456
    """
    # Set up theme and hyperlink preferences
    from flow.cli.utils.theme_manager import theme_manager
    from flow.cli.utils.hyperlink_support import hyperlink_support
    import os

    # Apply theme settings
    if theme:
        theme_manager.load_theme(theme)
    if no_color:
        os.environ["NO_COLOR"] = "1"

    # Apply hyperlink settings
    if hyperlinks is not None:
        os.environ["FLOW_HYPERLINKS"] = "1" if hyperlinks else "0"
        # Clear cache to force re-detection
        hyperlink_support._support_cached = None

    # Store settings in context for child commands
    ctx.ensure_object(dict)
    ctx.obj["theme"] = theme
    ctx.obj["no_color"] = no_color
    ctx.obj["hyperlinks"] = hyperlinks


def setup_cli():
    """Set up the CLI by registering all available commands.

    This function discovers and registers all command modules with the
    main CLI group. It supports both individual commands and command groups.

    Returns:
        click.Group: The configured CLI group with all commands registered.

    Raises:
        TypeError: If a command module returns an invalid command type.
    """
    commands = get_commands()

    for command in commands:
        cmd = command.get_command()

        if isinstance(cmd, (click.Command, click.Group)):
            cli.add_command(cmd)
        else:
            raise TypeError(f"Command {command.name} must return a click.Command or click.Group")

    return cli


cli = setup_cli()

# Enable automatic shell completion
try:
    from auto_click_auto import enable_click_shell_completion
    from auto_click_auto.constants import ShellType

    enable_click_shell_completion(
        program_name="flow",
        shells={ShellType.BASH, ShellType.ZSH, ShellType.FISH},
    )
except ImportError:
    # auto-click-auto not installed, fall back to manual completion
    pass


def main():
    """Entry point for the Flow CLI application.

    This function provides a unified interface on top of single-responsibility
    command modules, orchestrating all CLI commands through a central entry point.

    Returns:
        int: Exit code from the CLI execution.
    """
    # Quick config check on startup (can be disabled via env var)
    if os.environ.get("FLOW_SKIP_CONFIG_CHECK") != "1":
        # Only check for commands that need config (not init, help, etc)
        if len(sys.argv) > 1 and sys.argv[1] not in ["init", "--help", "-h", "--version"]:
            try:
                # Try to load config without auto_init to see if it's configured
                from flow.api.config import Config

                Config.from_env(require_auth=True)
            except ValueError:
                # Config missing - provide helpful guidance
                from flow.cli.utils.theme_manager import theme_manager

                console = theme_manager.create_console()
                console.print("[yellow]⚠ Flow SDK is not configured[/yellow]\n")
                console.print("To get started, run: [cyan]flow init[/cyan]")
                console.print("Or set FLOW_API_KEY environment variable\n")
                console.print("For help: [dim]flow --help[/dim]")
                return 1

    return cli()


if __name__ == "__main__":
    cli()
