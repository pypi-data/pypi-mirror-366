"""Dev command - Persistent development environment with container execution.

This module implements the dev command for the Flow CLI. It provides a
persistent VM with container-based command execution, similar to SLURM's
srun interface.

Command Usage:
    flow dev [OPTIONS]

Examples:
    Start or connect to dev VM:
        $ flow dev

    Execute command in container:
        $ flow dev -c 'python train.py'

    Reset all containers:
        $ flow dev --reset

    Stop dev VM:
        $ flow dev --stop

    Check status:
        $ flow dev --status

The dev environment provides:
- Persistent VM that runs throughout the day
- Fast container-based command execution
- Workspace synchronization
- Easy reset and cleanup
"""

import hashlib
import json
import logging
import os
import shlex
import time
import uuid
from typing import Optional, Dict, Any, TypedDict, List

import click

from flow import Flow, TaskConfig, ValidationError
from flow.api.models import TaskStatus, Task
from flow.errors import AuthenticationError, TaskNotFoundError

from .base import BaseCommand, console
from .utils import wait_for_task

logger = logging.getLogger(__name__)


class ContainerInfo(TypedDict):
    """Docker container information from 'docker ps --format json'."""
    
    Names: str
    Status: str
    Image: str
    Command: str
    CreatedAt: str
    ID: str


class ContainerStatus(TypedDict):
    """Container status information for dev VM."""
    
    active_containers: int
    containers: List[ContainerInfo]


class DevVMManager:
    """Manages the lifecycle of development VMs."""

    def __init__(self, flow_client: Flow):
        """Initialize VM manager.

        Args:
            flow_client: Flow SDK client instance
        """
        self.flow_client = flow_client
        self.dev_vm_prefix = "flow-dev"

    def get_dev_vm_name(self, force_unique: bool = False) -> str:
        """Generate consistent dev VM name for current user.

        Args:
            force_unique: If True, append a unique suffix to ensure uniqueness

        Returns:
            Unique dev VM name based on username
        """
        user = os.environ.get("USER", "default")
        # Create a short hash to ensure uniqueness
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        vm_name = f"dev-{name_hash}"

        if force_unique:
            # Add a short UUID suffix for uniqueness
            unique_suffix = uuid.uuid4().hex[:6]
            vm_name = f"{vm_name}-{unique_suffix}"

        logger.debug(f"Generated dev VM name: {vm_name} for user: {user}")
        return vm_name

    def find_dev_vm(self, include_not_ready=False):
        """Find existing dev VM for current user.

        Args:
            include_not_ready: If True, also return VMs without SSH access yet

        Returns:
            Task object if found, None otherwise
        """
        base_vm_name = self.get_dev_vm_name()
        # Build the expected dev VM prefix for this user
        user = os.environ.get("USER", "default")
        # The prefix matches our new naming pattern
        name_hash = hashlib.md5(f"{user}-dev".encode()).hexdigest()[:6]
        vm_prefix = f"dev-{name_hash}"
        
        # Also check for legacy naming pattern
        legacy_prefix = f"flow-dev-{user}"

        try:
            # List running tasks
            logger.debug(f"Searching for existing dev VM with prefix: {vm_prefix} or {legacy_prefix}")
            tasks = self.flow_client.list_tasks(status=TaskStatus.RUNNING)

            logger.debug(f"Found {len(tasks)} running tasks")

            # Find all tasks that match our dev VM naming patterns (old and new)
            # Since we can't reliably check config.env (it's not returned by list_tasks),
            # we rely on the naming convention which is unique per user
            dev_vm_candidates = []
            not_ready_vms = []
            
            for task in tasks:
                # Check both new and legacy naming patterns
                if task.name.startswith(vm_prefix) or task.name.startswith(legacy_prefix):
                    logger.debug(f"Found potential dev VM: {task.name} (ID: {task.task_id})")
                    # Separate ready and not-ready VMs
                    if task.ssh_host:
                        dev_vm_candidates.append(task)
                        logger.debug(f"  - Has SSH access: {task.ssh_host}:{task.ssh_port}")
                    else:
                        not_ready_vms.append(task)
                        logger.debug(f"  - No SSH access yet")

            # If we only have not-ready VMs and include_not_ready is True, return the newest
            if include_not_ready and not dev_vm_candidates and not_ready_vms:
                not_ready_vms.sort(key=lambda t: t.created_at, reverse=True)
                logger.info(f"Found {len(not_ready_vms)} dev VM(s) still provisioning")
                return not_ready_vms[0]

            if not dev_vm_candidates:
                logger.debug("No ready dev VMs found")
                return None

            # If we have multiple dev VMs, use the most recent one
            if len(dev_vm_candidates) > 1:
                logger.info(f"Found {len(dev_vm_candidates)} ready dev VMs - selecting most recent")
                # Sort by created_at timestamp (newest first)
                dev_vm_candidates.sort(key=lambda t: t.created_at, reverse=True)

            selected_vm = dev_vm_candidates[0]
            logger.info(f"Using existing dev VM: {selected_vm.name} (ID: {selected_vm.task_id})")
            return selected_vm

        except Exception as e:
            logger.warning(f"Error searching for dev VM: {e}")
            return None

    def create_dev_vm(self, instance_type: str = None, ssh_keys: list = None, max_price_per_hour: float = None) -> Task:
        """Create a new dev VM.

        Args:
            instance_type: GPU/CPU instance type
            ssh_keys: SSH keys for access
            max_price_per_hour: Maximum hourly price in USD

        Returns:
            Task object for the new VM
        """
        # First try with consistent name
        vm_name = self.get_dev_vm_name()

        # Default instance type for dev
        if not instance_type:
            instance_type = os.environ.get("FLOW_DEV_INSTANCE_TYPE", "h100")

        # Create VM configuration
        # For dev VMs, we use a startup script that installs Docker and then sleeps
        dev_startup_script = """#!/bin/bash
set -e

# Install Docker if not present
if ! command -v docker >/dev/null 2>&1; then
    echo "Installing Docker in dev container..."
    apt-get update -qq
    apt-get install -y -qq curl
    curl -fsSL https://get.docker.com | sh
    
    # Enable Docker service
    service docker start || true
    
    # Add permissions
    groupadd -f docker
    usermod -aG docker root || true
fi

# Install other dev tools
apt-get install -y -qq git vim htop

# Keep container running
exec sleep infinity
"""
        
        config_dict = {
            "name": vm_name,
            "instance_type": instance_type,
            "image": os.environ.get("FLOW_DEV_IMAGE", "nvidia/cuda:12.1.0-devel-ubuntu22.04"),
            "command": ["bash", "-c", dev_startup_script],
            "env": {
                "FLOW_DEV_VM": "true",
                "FLOW_DEV_USER": os.environ.get("USER", "default"),
                "DEBIAN_FRONTEND": "noninteractive",
            },
            "ssh_keys": ssh_keys or [],
            "priority": "high",  # High priority for dev VMs
        }
        
        # Add max_price_per_hour if specified
        if max_price_per_hour is not None:
            config_dict["max_price_per_hour"] = max_price_per_hour
            
        config = TaskConfig(**config_dict)

        # Submit task
        logger.info(f"Creating dev VM with instance type: {instance_type}")
        try:
            return self.flow_client.run(config)
        except Exception as e:
            error_msg = str(e)
            if "Name already used" in error_msg or "already exists" in error_msg.lower():
                # Name conflict - try with unique suffix
                logger.info("Dev VM name already in use, generating unique name")
                vm_name = self.get_dev_vm_name(force_unique=True)
                config.name = vm_name
                return self.flow_client.run(config)
            else:
                # Re-raise other errors
                raise

    def stop_dev_vm(self) -> bool:
        """Stop the dev VM.

        Returns:
            True if VM was stopped, False if not found
        """
        vm = self.find_dev_vm()
        if vm:
            self.flow_client.cancel(vm.task_id)
            return True
        return False


class DevContainerExecutor:
    """Executes commands in containers on the dev VM."""

    def __init__(self, flow_client: Flow, vm_task: Task):
        """Initialize container executor.

        Args:
            flow_client: Flow SDK client
            vm_task: The dev VM task object
        """
        self.flow_client = flow_client
        self.vm_task = vm_task
        self.container_prefix = "flow-dev-exec"

    def execute_command(self, command: str, image: str = None, interactive: bool = False) -> int:
        """Execute command in a new container on the dev VM.

        Args:
            command: Command to execute
            image: Docker image to use
            interactive: Whether to run interactively

        Returns:
            Exit code of the command
        """
        # Check if this is a system command that should run directly on the VM
        system_commands = [
            'nvidia-smi', 'gpustat', 'nvtop', 'lspci', 'lsusb', 
            'htop', 'top', 'ps', 'df', 'free', 'uptime', 
            'uname', 'hostname', 'whoami', 'pwd', 'ls', 'll',
            'cat', 'grep', 'awk', 'sed', 'find', 'which',
            'systemctl', 'service', 'journalctl', 'dmesg'
        ]
        
        # Parse the command to get the base command
        import shlex as shlex_parse
        try:
            parsed = shlex_parse.split(command)
            base_command = parsed[0] if parsed else ""
            # Handle cases like /usr/bin/nvidia-smi
            base_command = os.path.basename(base_command)
        except:
            base_command = command.split()[0] if command.split() else ""
            base_command = os.path.basename(base_command)
        
        # If it's a system command or no image is specified and it looks like a system command
        run_directly = base_command in system_commands or (
            not image and (
                command.startswith('sudo ') or
                command.startswith('/usr/') or
                command.startswith('/bin/') or
                command.startswith('/sbin/') or
                base_command in system_commands
            )
        )
        
        # Get remote operations from provider
        try:
            remote_ops = self.flow_client._provider.get_remote_operations()
        except AttributeError:
            # Fallback for providers without remote_operations
            console.print("[red]Error: Provider doesn't support remote operations[/red]")
            return 1

        if run_directly:
            # Execute directly on the VM without Docker
            logger.info(f"Executing system command directly: {command[:50]}...")
            
            if interactive:
                # Interactive execution using open_shell
                try:
                    remote_ops.open_shell(self.vm_task.task_id, command=command)
                    return 0
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    return 1
            else:
                # Non-interactive - use execute_command
                try:
                    from flow.providers.fcp.remote_operations import RemoteExecutionError
                    
                    output = remote_ops.execute_command(self.vm_task.task_id, command)
                    if output:
                        console.print(output, end="")
                    logger.debug("Command executed successfully")
                    return 0
                except RemoteExecutionError as e:
                    console.print(f"[red]Command failed: {e}[/red]")
                    return 1
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    return 1
        
        # Otherwise, run in Docker container as before
        # Generate unique container name
        container_name = f"{self.container_prefix}-{uuid.uuid4().hex[:8]}"

        # Default image
        if not image:
            image = os.environ.get("FLOW_DEV_CONTAINER_IMAGE", "ubuntu:22.04")

        # Build docker command
        docker_args = [
            "docker",
            "run",
            "--rm",  # Remove container after execution
            "--name",
            container_name,
            "-v",
            "/workspace:/workspace",  # Mount workspace
            "-w",
            "/workspace",  # Working directory
            "--pull",
            "missing",  # Pull image if not present
        ]

        # Add environment variables
        docker_args.extend(
            [
                "-e",
                "FLOW_DEV_CONTAINER=true",
                "-e",
                f"FLOW_DEV_USER={os.environ.get('USER', 'default')}",
            ]
        )

        # Add GPU support if available
        docker_args.extend(["--gpus", "all"])

        if interactive:
            docker_args.extend(["-it"])

        # Add image and command
        docker_args.append(image)
        docker_args.extend(["sh", "-c", command])

        # Build final command
        docker_cmd = "sudo " + " ".join(shlex.quote(arg) for arg in docker_args)

        # Execute via Flow's remote operations
        if interactive:
            # Interactive execution using open_shell
            try:
                remote_ops.open_shell(self.vm_task.task_id, command=docker_cmd)
                return 0
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return 1
        else:
            # Non-interactive - use execute_command
            try:
                from flow.providers.fcp.remote_operations import RemoteExecutionError

                # First, ensure image is available (pull if needed)
                logger.debug(f"Checking Docker image availability: {image}")
                try:
                    pull_output = remote_ops.execute_command(
                        self.vm_task.task_id,
                        f"sudo docker image inspect {image} >/dev/null 2>&1 || sudo docker pull {image}",
                    )
                    if pull_output and "Pulling from" in pull_output:
                        console.print(f"Pulling Docker image: {image}")
                        logger.info(f"Pulling Docker image: {image}")
                except RemoteExecutionError as e:
                    # Image pull might fail but container might still run with cached image
                    logger.debug(f"Image pull failed (may use cache): {e}")
                    pass

                # Execute the actual command
                logger.info(f"Executing container command: {command[:50]}...")
                output = remote_ops.execute_command(self.vm_task.task_id, docker_cmd)
                if output:
                    console.print(output, end="")
                logger.debug("Command executed successfully")
                return 0
            except RemoteExecutionError as e:
                error_msg = str(e)
                if "unable to find image" in error_msg.lower():
                    console.print(
                        f"[red]Docker image '{image}' not found and could not be pulled[/red]"
                    )
                    console.print(
                        "[yellow]Tip: Check image name or ensure internet connectivity on the dev VM[/yellow]"
                    )
                elif "docker: command not found" in error_msg.lower():
                    console.print("[red]Docker is not installed on the dev VM[/red]")
                    console.print("[yellow]Tip: SSH into the VM and install Docker first[/yellow]")
                else:
                    console.print(f"[red]Command failed: {e}[/red]")
                return 1
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return 1

    def reset_containers(self) -> None:
        """Reset all dev containers on the VM."""
        # Get remote operations from provider
        try:
            remote_ops = self.flow_client._provider.get_remote_operations()
        except AttributeError:
            console.print("[red]Error: Provider doesn't support remote operations[/red]")
            return

        # Commands to clean up containers
        cleanup_commands = [
            # Stop all flow-dev containers
            f"sudo docker ps -q -f name={self.container_prefix} | xargs -r sudo docker stop",
            # Remove stopped containers
            "sudo docker container prune -f",
            # Clean up dangling images
            "sudo docker image prune -f",
        ]

        for cmd in cleanup_commands:
            try:
                # Execute cleanup command using remote operations
                from flow.providers.fcp.remote_operations import RemoteExecutionError

                remote_ops.execute_command(self.vm_task.task_id, cmd)
            except RemoteExecutionError as e:
                # Some commands may fail if no containers exist - that's OK
                if "requires at least 1 argument" not in str(e):
                    console.print(f"[yellow]Warning during cleanup: {e}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Warning during cleanup: {e}[/yellow]")

    def get_container_status(self) -> ContainerStatus:
        """Get status of containers on the dev VM.

        Returns:
            ContainerStatus with count and detailed container information
        """
        # Get remote operations from provider
        try:
            remote_ops = self.flow_client._provider.get_remote_operations()
        except AttributeError:
            return {"active_containers": 0, "containers": []}

        # Get running containers
        list_cmd = f"sudo docker ps -f name={self.container_prefix} --format json"

        try:
            from flow.providers.fcp.remote_operations import RemoteExecutionError

            output = remote_ops.execute_command(self.vm_task.task_id, list_cmd)

            containers = []
            if output:
                for line in output.strip().split("\n"):
                    if line:
                        try:
                            containers.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass

            return {"active_containers": len(containers), "containers": containers}
        except RemoteExecutionError:
            return {"active_containers": 0, "containers": []}
        except Exception:
            return {"active_containers": 0, "containers": []}


class DevCommand(BaseCommand):
    """Development environment command implementation."""

    @property
    def name(self) -> str:
        return "dev"

    @property
    def help(self) -> str:
        return "Fast development environment - persistent VM with containerized execution"

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--command", "-c", help="Command to execute in container")
        @click.option(
            "--instance-type", "-i", help="Instance type for dev VM (e.g., a100, h100)"
        )
        @click.option("--image", help="Docker image for container execution")
        @click.option(
            "--ssh-keys", "-k", multiple=True, help="SSH keys to use (can specify multiple)"
        )
        @click.option("--reset", "-r", is_flag=True, help="Reset all containers")
        @click.option("--stop", "-s", is_flag=True, help="Stop the dev VM")
        @click.option("--status", is_flag=True, help="Show dev environment status")
        @click.option("--force-new", is_flag=True, help="Force creation of new dev VM")
        @click.option("--max-price-per-hour", "-m", type=float, help="Maximum hourly price in USD")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed examples and workflows")
        def dev(
            command: Optional[str],
            instance_type: Optional[str],
            image: Optional[str],
            ssh_keys: tuple,
            reset: bool,
            stop: bool,
            status: bool,
            force_new: bool,
            max_price_per_hour: Optional[float],
            verbose: bool,
        ):
            """Manage persistent development environment.

            \b
            Examples:
                flow dev                     # Start/connect to dev VM
                flow dev -c 'python train.py'  # Run in container
                flow dev -c bash             # Interactive session
                flow dev --stop              # Stop dev VM

            Use 'flow dev --verbose' for advanced workflows and container patterns.
            """
            if verbose:
                console.print("\n[bold]Development Environment Workflows:[/bold]\n")
                console.print("Basic usage:")
                console.print("  flow dev                          # Start persistent VM")
                console.print("  flow dev -c 'python script.py'    # Run command in container")
                console.print("  flow dev -c bash                  # Interactive shell")
                console.print("  flow dev --status                 # Check VM status\n")
                
                console.print("Container management:")
                console.print("  flow dev --reset                  # Reset all containers")
                console.print("  flow dev --stop                   # Stop dev VM")
                console.print("  flow dev --force-new              # Create fresh VM\n")
                
                console.print("Custom environments:")
                console.print("  flow dev -c 'make test' --image python:3.11")
                console.print("  flow dev -c 'cargo build' --image rust:latest")
                console.print("  flow dev -i a100 -c 'python train.py'  # GPU dev\n")
                
                console.print("Advanced patterns:")
                console.print("  # Long-running notebook server")
                console.print("  flow dev -c 'jupyter lab --ip=0.0.0.0'")
                console.print("  ")
                console.print("  # Data preprocessing pipeline")
                console.print("  flow dev -c 'python preprocess.py && python analyze.py'")
                console.print("  ")
                console.print("  # Interactive debugging")
                console.print("  flow dev -c 'python -m pdb train.py'\n")
                
                console.print("Key benefits:")
                console.print("  • VM persists between commands (no startup delay)")
                console.print("  • Containers start in ~2 seconds")
                console.print("  • Shared workspace and cache")
                console.print("  • Cost-effective for iterative development\n")
                return
                
            self._execute(
                command, instance_type, image, ssh_keys, reset, stop, 
                status, force_new, max_price_per_hour
            )

        return dev

    def _execute(
        self,
        command: Optional[str],
        instance_type: Optional[str],
        image: Optional[str],
        ssh_keys: tuple,
        reset: bool,
        stop: bool,
        status: bool,
        force_new: bool,
        max_price_per_hour: Optional[float],
    ) -> None:
        """Execute the dev command."""
        # Start animation immediately for all modes except stop/status
        from ..utils.animated_progress import AnimatedEllipsisProgress

        progress = None
        if not stop and not status:
            # Start animation immediately for both command and interactive modes
            initial_msg = "Starting flow dev"
            if command:
                # Show a preview of the command being run
                cmd_preview = command if len(command) <= 30 else command[:27] + "..."
                initial_msg = f"Preparing to run: {cmd_preview}"

            progress = AnimatedEllipsisProgress(
                console, initial_msg, transient=True, start_immediately=True
            )

        try:
            # Initialize Flow client and VM manager
            flow_client = Flow()
            vm_manager = DevVMManager(flow_client)

            # Handle stop command
            if stop:
                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Stopping dev VM", start_immediately=True
                ) as progress:
                    if vm_manager.stop_dev_vm():
                        console.print("[green]✓[/green] Dev VM stopped successfully")
                    else:
                        console.print("[yellow]No dev VM found[/yellow]")
                return

            # Handle status command
            if status:
                if progress:
                    progress.__exit__(None, None, None)
                self._show_status(vm_manager, flow_client)
                return

            # Find or create dev VM
            vm = vm_manager.find_dev_vm()

            if force_new and vm:
                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Force stopping existing dev VM", start_immediately=True
                ) as progress:
                    vm_manager.stop_dev_vm()
                    vm = None

            # If no ready VM, check if there's one provisioning
            if not vm:
                vm_provisioning = vm_manager.find_dev_vm(include_not_ready=True)
                if vm_provisioning:
                    # Found a VM that's still provisioning
                    if progress:
                        progress.update_message(f"Found dev VM provisioning: {vm_provisioning.name}")
                        time.sleep(0.5)
                        progress.__exit__(None, None, None)
                        progress = None
                    
                    console.print(f"[yellow]Found dev VM still provisioning: {vm_provisioning.name}[/yellow]")
                    
                    # Wait for it to be ready (similar to flow ssh)
                    self._wait_for_vm_ready(flow_client, vm_provisioning)
                    vm = vm_provisioning

            if not vm:
                # Update existing progress or create new one
                if progress:
                    progress.update_message(f"Creating new dev VM ({instance_type or 'h100'})")
                    # Give a moment for the message to show
                    import time

                    time.sleep(0.3)
                    # Stop the initial progress as we'll use a new one for creation
                    progress.__exit__(None, None, None)
                    progress = None
                else:
                    console.print("Starting new dev VM...")

                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console,
                    f"Creating dev VM ({instance_type or 'h100'})",
                    transient=True,
                    start_immediately=True,
                ):
                    vm = vm_manager.create_dev_vm(
                        instance_type=instance_type, 
                        ssh_keys=list(ssh_keys) if ssh_keys else None,
                        max_price_per_hour=max_price_per_hour
                    )

                # Wait for VM to be ready with better error handling
                try:
                    # wait_for_task already uses AnimatedEllipsisProgress internally
                    final_status = wait_for_task(flow_client, vm.task_id, watch=False)

                    if final_status != "running":
                        # Get task details for error diagnosis
                        try:
                            task = flow_client.get_task(vm.task_id)
                            if hasattr(task, "message") and task.message:
                                console.print(
                                    f"[red]✗[/red] Failed to start dev VM: {task.message}"
                                )
                            else:
                                console.print(
                                    f"[red]✗[/red] Failed to start dev VM (status: {final_status})"
                                )
                        except:
                            console.print(
                                f"[red]✗[/red] Failed to start dev VM (status: {final_status})"
                            )

                        # Cleanup failed VM
                        try:
                            flow_client.cancel(vm.task_id)
                        except:
                            pass
                        return
                except KeyboardInterrupt:
                    console.print("\n[yellow]Cancelled VM startup[/yellow]")
                    # Cleanup the VM being created
                    try:
                        from ..utils.animated_progress import AnimatedEllipsisProgress

                        with AnimatedEllipsisProgress(
                            console, "Cleaning up partially created VM"
                        ) as progress:
                            flow_client.cancel(vm.task_id)
                    except:
                        pass
                    raise SystemExit(1)

                console.print(f"[green]✓[/green] Dev VM started: {vm.name}")

                # Wait for IP assignment and SSH readiness
                vm = self._wait_for_vm_ready(flow_client, vm)
            else:
                # Update progress message with VM info if we have a progress indicator
                if progress:
                    progress.update_message(f"Using existing dev VM: {vm.name}")
                    # Give the animation a moment to display the update
                    import time

                    time.sleep(0.5)
                else:
                    console.print(f"Using existing dev VM: {vm.name}")

            # Create container executor
            executor = DevContainerExecutor(flow_client, vm)

            # Handle reset command
            if reset:
                from ..utils.animated_progress import AnimatedEllipsisProgress

                with AnimatedEllipsisProgress(
                    console, "Resetting all dev containers", start_immediately=True
                ) as progress:
                    executor.reset_containers()
                console.print("[green]✓[/green] Containers reset successfully")
                return

            # Handle command execution
            if command:
                # Check if command is interactive
                interactive_commands = [
                    "bash",
                    "sh",
                    "zsh",
                    "fish",
                    "python",
                    "ipython",
                    "irb",
                    "node",
                ]
                is_interactive = command.strip() in interactive_commands

                # Update progress message with more specific info
                if progress:
                    # Keep the progress running while we prepare
                    progress.update_message("Preparing container environment")

                    # Let it show for a moment before transitioning
                    import time

                    time.sleep(0.3)

                    # Stop progress before executing command
                    progress.__exit__(None, None, None)
                    progress = None  # Mark as stopped

                # Now print the message after stopping animation
                if is_interactive:
                    console.print(f"Starting interactive session: {command}")
                else:
                    console.print(f"Executing: {command}")

                exit_code = executor.execute_command(
                    command, image=image, interactive=is_interactive
                )

                if exit_code != 0 and not is_interactive:
                    raise SystemExit(exit_code)
            else:
                # No command - connect interactively to VM
                # Progress is already started at the beginning for interactive mode
                if progress:
                    # Update message and add info about persistent environment
                    progress.update_message("Connecting to dev VM")

                    # Stop the progress briefly to print the info message
                    progress.__exit__(None, None, None)
                    console.print(
                        "[dim]Once connected, you'll have a persistent Ubuntu environment[/dim]"
                    )

                    # Start a new progress for the actual connection
                    progress = AnimatedEllipsisProgress(
                        console, "Connecting to dev VM", transient=True, start_immediately=True
                    )
                else:
                    # Fallback if no progress was started
                    console.print(
                        "[dim]Once connected, you'll have a persistent Ubuntu environment[/dim]"
                    )
                    progress = AnimatedEllipsisProgress(
                        console, "Connecting to dev VM", transient=True, start_immediately=True
                    )

                # Pass progress context to shell so it can be properly closed before subprocess
                flow_client.shell(vm.task_id, progress_context=progress)

            # Show helpful next actions
            if not command or command in interactive_commands:
                self.show_next_actions(
                    [
                        "Run a command: [cyan]flow dev -c 'python script.py'[/cyan]",
                        "Reset containers: [cyan]flow dev --reset[/cyan]",
                        "Check status: [cyan]flow dev --status[/cyan]",
                    ]
                )

        except AuthenticationError:
            self.handle_auth_error()
        except TaskNotFoundError as e:
            self.handle_error(f"Dev VM not found: {e}")
        except ValidationError as e:
            self.handle_error(f"Invalid configuration: {e}")
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            raise SystemExit(1)
        except Exception as e:
            # More specific error handling for common issues
            error_msg = str(e)
            if "connection refused" in error_msg.lower():
                self.handle_error(
                    "Cannot connect to Docker daemon. Ensure Docker is installed and running on the dev VM.\n"
                    "You may need to SSH into the VM and install Docker: [cyan]flow dev[/cyan]"
                )
            elif "no such image" in error_msg.lower():
                self.handle_error(
                    f"Docker image not found: {image or 'default'}\n"
                    "The image will be pulled automatically on first use."
                )
            else:
                self.handle_error(str(e))
        finally:
            # Ensure progress animation is stopped if it was started
            if progress and hasattr(progress, "_active") and progress._active:
                progress.__exit__(None, None, None)

    def _show_status(self, vm_manager: DevVMManager, flow_client: Flow) -> None:
        """Show dev environment status."""
        vm = vm_manager.find_dev_vm()

        if not vm:
            console.print("[yellow]No dev VM running[/yellow]")
            console.print("\nStart a dev VM with: [cyan]flow dev[/cyan]")
            return

        # Get VM details
        console.print(f"\n[bold]Dev VM Status[/bold]")
        console.print(f"Name: [cyan]{vm.name}[/cyan]")
        console.print(f"ID: [dim]{vm.task_id}[/dim]")
        console.print(f"Status: [green]Running[/green]")
        console.print(f"Instance: {vm.instance_type}")

        if vm.started_at:
            from datetime import datetime, timezone

            uptime = datetime.now(timezone.utc) - vm.started_at
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            console.print(f"Uptime: {hours}h {minutes}m")

        # Get container status
        try:
            executor = DevContainerExecutor(flow_client, vm)
            container_status = executor.get_container_status()

            console.print(f"\n[bold]Containers[/bold]")
            console.print(f"Active: {container_status['active_containers']}")

            if container_status["containers"]:
                console.print("\nRunning containers:")
                for container in container_status["containers"]:
                    console.print(
                        f"  - {container.get('Names', 'unknown')} ({container.get('Status', 'unknown')})"
                    )
        except Exception:
            console.print("\n[dim]Unable to fetch container status[/dim]")

    def _wait_for_vm_ready(self, flow_client: Flow, vm: Task) -> Task:
        """Wait for dev VM to have IP assignment and be ready for connections.

        Args:
            flow_client: Flow client instance
            vm: VM task object
            
        Returns:
            Updated VM task object with SSH info
        """
        from flow.providers.fcp.ssh_utils import wait_for_task_ssh_info, SSHNotReadyError, check_task_age_for_ssh

        # Check if VM already has IP
        if vm.ssh_host:
            return vm

        # Check task age to provide appropriate message
        age_message = check_task_age_for_ssh(vm)
        
        if age_message and "unexpected" in age_message:
            # Instance has been running for a while without SSH
            console.print(f"\n[red]{age_message}[/red]")
            console.print("\nPossible issues:")
            console.print("  • Instance may have been preempted or terminated")
            console.print("  • SSH service may have crashed")
            console.print("  • Network configuration issues")
            console.print("\nRecommended actions:")
            console.print(
                f"  • Check instance health: [cyan]flow health {vm.name or vm.task_id}[/cyan]"
            )
            console.print(f"  • View logs: [cyan]flow logs {vm.name or vm.task_id}[/cyan]")
            console.print(
                f"  • Consider restarting: [cyan]flow cancel {vm.name or vm.task_id} && flow dev[/cyan]"
            )
            raise SystemExit(1)
        else:
            # Instance might still be provisioning - wait for IP assignment
            from flow.providers.fcp.core.constants import EXPECTED_PROVISION_MINUTES

            console.print(
                f"\n[yellow]Instance is provisioning[/yellow] (waiting for IP assignment)"
            )
            console.print(
                f"This can take up to {EXPECTED_PROVISION_MINUTES} minutes for FCP instances."
            )
            if age_message:
                console.print(age_message)
            console.print("[dim]Press Ctrl+C to cancel[/dim]\n")

        try:
            # Get provider instance
            provider = (
                flow_client._get_provider() if hasattr(flow_client, "_get_provider") else None
            )

            # Use shared utility to wait for SSH info - it will show AnimatedEllipsisProgress
            vm = wait_for_task_ssh_info(
                task=vm,
                provider=provider,
                timeout=1200,  # 20 minutes for dev VMs
                show_progress=True,  # This will use built-in AnimatedEllipsisProgress
            )

            if vm.ssh_host:
                console.print("[green]✓[/green] Dev VM is ready!")

        except SSHNotReadyError as e:
            console.print(f"\n[red]✗ {str(e)}[/red]")
            if "interrupted by user" in str(e).lower():
                console.print("\n[yellow]Wait cancelled by user[/yellow]")
                console.print("\nThe dev VM may still be provisioning. You can check later with:")
                console.print(f"  [cyan]flow dev[/cyan]")
                console.print(f"  [cyan]flow status {vm.name or vm.task_id}[/cyan]")
            else:
                console.print("\nPossible issues:")
                console.print("  • Instance is stuck in provisioning")
                console.print("  • Cloud provider resource limits reached")
                console.print("  • Network configuration issues")
                console.print(f"\nCheck VM status: [cyan]flow status {vm.task_id}[/cyan]")
            raise SystemExit(1)

        # Give SSH a moment to fully initialize after IP assignment
        from ..utils.animated_progress import AnimatedEllipsisProgress

        with AnimatedEllipsisProgress(
            console, "Initializing SSH connection", transient=True
        ):
            time.sleep(2)
            
        return vm


# Export command instance
command = DevCommand()
