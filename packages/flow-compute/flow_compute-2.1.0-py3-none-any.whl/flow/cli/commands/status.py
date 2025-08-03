"""Status command - List and monitor GPU compute tasks.

This module implements the status command for the Flow CLI. It provides a
comprehensive view of submitted tasks, with filtering and display options
for monitoring task execution and resource usage.

Examples:
    # Check all your recent tasks
    $ flow status

    # Monitor a specific task by name or ID
    $ flow status my-training-job

    # Show only running tasks with costs
    $ flow status --status running

Command Usage:
    flow status [TASK_ID_OR_NAME] [OPTIONS]

Status values:
- pending: Task submitted, waiting for resources
- running: Task actively executing on GPU
- preempting: Task running but will be terminated soon by provider
- completed: Task finished successfully
- failed: Task terminated with error
- cancelled: Task cancelled by user

The command will:
- Query tasks from the configured provider
- Apply status and time filters
- Format output in a readable table
- Show task IDs, status, GPU type, and timing
- Display creation and completion timestamps

Output includes:
- Task ID (shortened for readability)
- Current status with color coding
- GPU type allocated
- Creation timestamp
- Duration or completion time

Note:
    By default, shows tasks from the last 24 hours plus any currently
    running or pending tasks (regardless of age). Use --all to see the
    complete task history.
"""

import os
import time
from typing import Optional

import click
from rich.progress import Progress, SpinnerColumn, TextColumn

from flow import Flow
from flow.api.models import TaskStatus
from flow.errors import AuthenticationError

from .base import BaseCommand, console
from ..utils.task_presenter import TaskPresenter, DisplayOptions
from ..utils.animated_progress import AnimatedEllipsisProgress


class StatusCommand(BaseCommand):
    """List tasks with optional filtering."""

    def __init__(self):
        """Initialize command with task presenter."""
        super().__init__()
        self.task_presenter = TaskPresenter(console)

    @property
    def name(self) -> str:
        return "status"

    @property
    def help(self) -> str:
        return "List and monitor GPU compute tasks - filter by status, name, or time"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.argument("task_identifier", required=False)
        @click.option("--all", "show_all", is_flag=True, help="Show all tasks (default: last 24h)")
        @click.option(
            "--status",
            "-s",
            type=click.Choice(
                ["pending", "running", "paused", "preempting", "completed", "failed", "cancelled"]
            ),
            help="Filter by status",
        )
        @click.option("--limit", default=20, help="Maximum number of tasks to show")
        @click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed status information and filtering examples")
        def status(
            task_identifier: Optional[str], show_all: bool, status: Optional[str], limit: int, output_json: bool, verbose: bool
        ):
            """List recent tasks or show details for a specific task.

            \b
            Examples:
                flow status                  # Recent tasks (last 24h)
                flow status my-training      # Find task by name
                flow status --status running # Only running tasks
                flow status --all            # Show all tasks

            Use 'flow status --verbose' for advanced filtering and monitoring patterns.
            """
            if verbose and not task_identifier:
                console.print("\n[bold]Task Status and Monitoring:[/bold]\n")
                console.print("Filtering options:")
                console.print("  flow status --all                 # Show all tasks (not just 24h)")
                console.print("  flow status --status running      # Filter by status")
                console.print("  flow status --status pending      # Tasks waiting for resources")
                console.print("  flow status --limit 50            # Show more results\n")
                
                console.print("Task details:")
                console.print("  flow status task-abc123           # View specific task")
                console.print("  flow status my-training           # Find by name")
                console.print("  flow status training-v2           # Partial name match\n")
                
                console.print("Status values:")
                console.print("  • pending     - Waiting for resources")
                console.print("  • running     - Actively executing")
                console.print("  • paused      - Temporarily stopped (no billing)")
                console.print("  • preempting  - Will be terminated soon")
                console.print("  • completed   - Finished successfully")
                console.print("  • failed      - Terminated with error")
                console.print("  • cancelled   - Cancelled by user\n")
                
                console.print("Monitoring workflows:")
                console.print("  # Watch task progress")
                console.print("  watch -n 5 'flow status --status running'")
                console.print("  ")
                console.print("  # Export for analysis")
                console.print("  flow status --all --json > tasks.json")
                console.print("  ")
                console.print("  # Check failed tasks")
                console.print("  flow status --status failed --limit 10\n")
                
                console.print("Next actions:")
                console.print("  • View logs: flow logs <task-name>")
                console.print("  • Connect: flow ssh <task-name>")
                console.print("  • Cancel: flow cancel <task-name>")
                console.print("  • Check health: flow health --task <task-name>\n")
                return
                
            self._execute(task_identifier, show_all, status, limit, output_json)

        return status

    def _execute(
        self, task_identifier: Optional[str], show_all: bool, status: Optional[str], limit: int, output_json: bool
    ) -> None:
        """Execute the status command."""
        # JSON output mode - no animation
        if output_json:
            import json
            flow_client = Flow()
            
            if task_identifier:
                # Single task lookup
                from ..utils.task_resolver import resolve_task_identifier
                task, error = resolve_task_identifier(flow_client, task_identifier)
                
                if error:
                    result = {"error": error}
                else:
                    result = {
                        "task_id": task.task_id,
                        "name": task.name,
                        "status": task.status.value,
                        "instance_type": task.instance_type,
                        "num_instances": getattr(task, 'num_instances', 1),
                        "region": task.region,
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "ssh_host": task.ssh_host
                    }
                
                console.print(json.dumps(result))
                return
            else:
                # Task list
                from ..utils.task_fetcher import TaskFetcher
                fetcher = TaskFetcher(flow_client)
                tasks = fetcher.fetch_for_display(show_all=show_all, status_filter=status, limit=limit)
                
                result = {
                    "tasks": [
                        {
                            "task_id": task.task_id,
                            "name": task.name,
                            "status": task.status.value,
                            "instance_type": task.instance_type,
                            "num_instances": getattr(task, 'num_instances', 1),
                            "created_at": task.created_at.isoformat() if task.created_at else None
                        }
                        for task in tasks
                    ]
                }
                
                console.print(json.dumps(result))
                return
        
        # Start animation immediately for instant feedback
        progress = AnimatedEllipsisProgress(
            console,
            "Fetching tasks" if not task_identifier else "Looking up task",
            start_immediately=True,
        )

        try:
            # Handle specific task request
            if task_identifier:
                with progress:
                    if not self.task_presenter.present_single_task(task_identifier):
                        return
            else:
                # Present task list with options
                display_options = DisplayOptions(
                    show_all=show_all, status_filter=status, limit=limit, show_details=True
                )

                with progress:
                    summary = self.task_presenter.present_task_list(display_options)

                # Show context-aware recommendations based on task states
                if summary:
                    recommendations = []
                    
                    # Dynamic help based on number of tasks shown
                    task_count = min(summary.total_shown, limit)
                    index_help = f":1-{task_count}" if task_count > 1 else ":1"
                    
                    # Check task states for context-aware recommendations
                    has_running = summary.running_tasks > 0
                    has_pending = summary.pending_tasks > 0
                    has_paused = summary.paused_tasks > 0
                    has_failed = summary.failed_tasks > 0
                    
                    if has_running:
                        recommendations.append(
                            f"SSH into running task: [cyan]flow ssh <task-name>[/cyan] or [cyan]flow ssh {index_help}[/cyan]"
                        )
                        recommendations.append(
                            f"View logs for a task: [cyan]flow logs <task-name>[/cyan] or [cyan]flow logs {index_help}[/cyan]"
                        )
                    
                    if has_pending:
                        recommendations.append(
                            f"Check pending task details: [cyan]flow status <task-name>[/cyan]"
                        )
                        if has_pending and not has_running:
                            recommendations.append(
                                "View all available resources: [cyan]flow status --all[/cyan]"
                            )
                    
                    if has_paused:
                        recommendations.append(
                            f"Resume paused task: [cyan]flow grab <task-name>[/cyan]"
                        )
                    
                    if has_failed:
                        recommendations.append(
                            f"Debug failed task: [cyan]flow logs <failed-task-name>[/cyan]"
                        )
                    
                    # Always include new task submission
                    if len(recommendations) < 3:
                        recommendations.append("Submit a new task: [cyan]flow run task.yaml[/cyan]")
                    
                    # If no active tasks, show getting started options
                    if summary.active_tasks == 0:
                        recommendations = [
                            "Submit a new task: [cyan]flow run task.yaml[/cyan]",
                            "Start development environment: [cyan]flow dev[/cyan]",
                            "View examples: [cyan]flow example[/cyan]",
                        ]
                    
                    if recommendations:
                        self.show_next_actions(recommendations[:3])  # Show top 3 recommendations

        except AuthenticationError:
            self.handle_auth_error()
        except Exception as e:
            self.handle_error(str(e))


# Export command instance
command = StatusCommand()
