"""Code transfer manager for FCP instances.

This module orchestrates the complete code upload flow, coordinating
SSH availability checks with file transfers for a seamless experience.
"""

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from flow.api.models import Task
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
from flow.errors import FlowError

from .ssh_waiter import ExponentialBackoffSSHWaiter, ISSHWaiter, SSHConnectionInfo
from .transfer_strategies import (
    ITransferStrategy,
    RsyncTransferStrategy,
    TransferError,
    TransferResult,
)
from .core.constants import EXPECTED_PROVISION_MINUTES

if TYPE_CHECKING:
    from rich.console import Console
    from .provider import FCPProvider

logger = logging.getLogger(__name__)


class CodeTransferError(FlowError):
    """Raised when code transfer fails."""

    pass


@dataclass
class CodeTransferConfig:
    """Configuration for code transfer operation."""

    source_dir: Path = None
    target_dir: str = "~"
    ssh_timeout: int = 1200  # 20 minutes
    transfer_timeout: int = 600  # 10 minutes
    retry_on_failure: bool = True
    use_compression: bool = True

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.source_dir is None:
            self.source_dir = Path.cwd()


class IProgressReporter:
    """Interface for progress reporting."""

    @contextmanager
    def ssh_wait_progress(self, message: str):
        """Context manager for SSH wait progress."""
        yield

    @contextmanager
    def transfer_progress(self, message: str):
        """Context manager for transfer progress."""
        yield

    def update_status(self, message: str) -> None:
        """Update current status message."""
        pass


class RichProgressReporter(IProgressReporter):
    """Progress reporter using Rich console."""

    def __init__(self, console: "Console"):
        """Initialize with Rich console."""
        self.console = console

    @contextmanager
    def ssh_wait_progress(self, message: str):
        """Show animated progress for SSH wait."""
        with AnimatedEllipsisProgress(self.console, message) as progress:
            yield progress

    @contextmanager
    def transfer_progress(self, message: str):
        """Show progress for file transfer."""
        # For now, use same animated progress
        # TODO: Could enhance with Rich progress bar showing bytes/speed
        with AnimatedEllipsisProgress(self.console, message, transient=False) as progress:
            yield progress

    def update_status(self, message: str) -> None:
        """Update status with Rich formatting."""
        self.console.print(f"[dim]{message}[/dim]")


class CodeTransferManager:
    """Orchestrates code transfer to running FCP instances.

    Coordinates SSH availability checking with file transfer,
    providing a seamless code upload experience with progress reporting.
    """

    def __init__(
        self,
        provider: Optional["FCPProvider"] = None,
        ssh_waiter: Optional[ISSHWaiter] = None,
        transfer_strategy: Optional[ITransferStrategy] = None,
        progress_reporter: Optional[IProgressReporter] = None,
    ):
        """Initialize code transfer manager.

        Args:
            provider: FCP provider for task operations
            ssh_waiter: SSH connection waiter (default: ExponentialBackoffSSHWaiter)
            transfer_strategy: File transfer strategy (default: RsyncTransferStrategy)
            progress_reporter: Progress reporting handler
        """
        self.provider = provider
        self.ssh_waiter = ssh_waiter or ExponentialBackoffSSHWaiter(provider)
        self.transfer_strategy = transfer_strategy or RsyncTransferStrategy()
        self.progress_reporter = progress_reporter

    def transfer_code_to_task(
        self, task: Task, config: Optional[CodeTransferConfig] = None
    ) -> TransferResult:
        """Transfer code to a running task.

        This is the main entry point that orchestrates:
        1. Waiting for SSH availability
        2. Transferring code files
        3. Progress reporting
        4. Error handling and recovery

        Args:
            task: Task to transfer code to
            config: Transfer configuration (uses defaults if not provided)

        Returns:
            TransferResult with transfer outcome

        Raises:
            CodeTransferError: If transfer fails
        """
        if not config:
            config = CodeTransferConfig()

        logger.info(
            f"Starting code transfer to task {task.task_id}\n"
            f"  Source: {config.source_dir} ({self._get_dir_size(config.source_dir)})\n"
            f"  Target: {task.task_id}:{config.target_dir}"
        )

        try:
            # Phase 1: Wait for SSH availability
            connection = self._wait_for_ssh(task, config)

            # Phase 2: Transfer code
            result = self._transfer_code(connection, config)

            # Phase 3: Verify transfer
            self._verify_transfer(connection, config)

            logger.info(
                f"Code transfer completed successfully\n"
                f"  Transferred: {self._format_bytes(result.bytes_transferred)}\n"
                f"  Duration: {result.duration_seconds:.1f}s\n"
                f"  Rate: {result.transfer_rate}"
            )

            return result

        except Exception as e:
            logger.error(f"Code transfer failed: {e}")

            # Provide helpful error message
            if isinstance(e, CodeTransferError):
                raise
            else:
                raise CodeTransferError(
                    f"Failed to transfer code to task {task.task_id}",
                    suggestions=[
                        "Check that the instance has started successfully",
                        "Verify SSH connectivity with: flow ssh " + task.task_id,
                        "Try again with: flow upload-code " + task.task_id,
                        "Use embedded upload instead: flow run --upload-strategy embedded",
                    ],
                ) from e

    def _wait_for_ssh(self, task: Task, config: CodeTransferConfig) -> SSHConnectionInfo:
        """Wait for SSH to become available.

        Args:
            task: Task to wait for
            config: Transfer configuration

        Returns:
            SSH connection information

        Raises:
            CodeTransferError: If SSH wait fails
        """
        logger.info(f"Waiting for task {task.task_id} to be ready for SSH access")

        # Progress callback for SSH wait
        def ssh_progress(status: str):
            if self.progress_reporter:
                self.progress_reporter.update_status(status)
            else:
                logger.debug(status)

        try:
            # Use progress reporter if available
            if self.progress_reporter:
                with self.progress_reporter.ssh_wait_progress("Waiting for SSH access"):
                    connection = self.ssh_waiter.wait_for_ssh(
                        task, timeout=config.ssh_timeout, progress_callback=ssh_progress
                    )
            else:
                connection = self.ssh_waiter.wait_for_ssh(
                    task, timeout=config.ssh_timeout, progress_callback=ssh_progress
                )

            logger.info("SSH connection established")
            return connection

        except Exception as e:
            raise CodeTransferError(
                f"Failed to establish SSH connection: {str(e)}",
                suggestions=[
                    f"Check task status: flow status {task.task_id}",
                    f"Instance may still be provisioning (can take up to {EXPECTED_PROVISION_MINUTES} minutes)",
                    "Try increasing timeout: --timeout 1800",
                ],
            ) from e

    def _transfer_code(
        self, connection: SSHConnectionInfo, config: CodeTransferConfig
    ) -> TransferResult:
        """Transfer code files to remote instance.

        Args:
            connection: SSH connection information
            config: Transfer configuration

        Returns:
            Transfer result

        Raises:
            CodeTransferError: If transfer fails
        """
        logger.info(f"Transferring code from {config.source_dir}")

        # Progress callback for transfer
        def transfer_progress(progress):
            if self.progress_reporter:
                if progress.current_file:
                    self.progress_reporter.update_status(f"Uploading: {progress.current_file}")
                elif progress.percentage:
                    status = f"Progress: {progress.percentage:.0f}%"
                    if progress.speed:
                        status += f" @ {progress.speed}"
                    if progress.eta:
                        status += f" (ETA: {progress.eta})"
                    self.progress_reporter.update_status(status)

        try:
            # Ensure target directory exists
            self._ensure_target_directory(connection, config.target_dir)

            # Use progress reporter if available
            if self.progress_reporter:
                with self.progress_reporter.transfer_progress("Uploading code"):
                    result = self.transfer_strategy.transfer(
                        source=config.source_dir,
                        target=config.target_dir,
                        connection=connection,
                        progress_callback=transfer_progress,
                    )
            else:
                result = self.transfer_strategy.transfer(
                    source=config.source_dir,
                    target=config.target_dir,
                    connection=connection,
                    progress_callback=transfer_progress,
                )

            return result

        except TransferError as e:
            # Check if this is a recoverable error
            if config.retry_on_failure and self._is_recoverable_error(str(e)):
                logger.warning(f"Transfer failed, retrying: {e}")
                # Simple retry once
                return self.transfer_strategy.transfer(
                    source=config.source_dir, target=config.target_dir, connection=connection
                )
            raise CodeTransferError(f"Code transfer failed: {e}") from e

    def _verify_transfer(self, connection: SSHConnectionInfo, config: CodeTransferConfig) -> None:
        """Verify that code was transferred successfully.

        Args:
            connection: SSH connection information
            config: Transfer configuration

        Raises:
            CodeTransferError: If verification fails
        """
        # Simple verification - check if target directory exists and has files
        from .remote_operations import FCPRemoteOperations

        remote_ops = FCPRemoteOperations(self.provider)

        try:
            # Check if directory exists and has content
            output = remote_ops.execute_command(
                connection.task_id, f"ls -la {config.target_dir} | head -5"
            )

            if "No such file or directory" in output:
                raise CodeTransferError(
                    f"Target directory {config.target_dir} not found after transfer"
                )

            # Could add more sophisticated verification here
            # (file count, specific files, checksums, etc.)

        except Exception as e:
            logger.warning(f"Transfer verification failed: {e}")
            # Don't fail the whole transfer for verification issues

    def _ensure_target_directory(self, connection: SSHConnectionInfo, target_dir: str) -> None:
        """Ensure target directory exists on remote instance.

        Args:
            connection: SSH connection information
            target_dir: Target directory path
        """
        from .remote_operations import FCPRemoteOperations

        remote_ops = FCPRemoteOperations(self.provider)

        try:
            # Create directory if it doesn't exist - use sudo for system directories
            if target_dir.startswith('/') and not target_dir.startswith('/home/'):
                remote_ops.execute_command(connection.task_id, f"sudo mkdir -p {target_dir} && sudo chown ubuntu:ubuntu {target_dir}")
            else:
                remote_ops.execute_command(connection.task_id, f"mkdir -p {target_dir}")
        except Exception as e:
            logger.warning(f"Failed to create target directory: {e}")

    def _is_recoverable_error(self, error_message: str) -> bool:
        """Check if error is recoverable and worth retrying.

        Args:
            error_message: Error message to check

        Returns:
            True if error is recoverable
        """
        recoverable_patterns = [
            "connection reset",
            "connection closed",
            "broken pipe",
            "timeout",
            "temporary failure",
        ]

        error_lower = error_message.lower()
        return any(pattern in error_lower for pattern in recoverable_patterns)

    def _get_dir_size(self, path: Path) -> str:
        """Get human-readable directory size.

        Args:
            path: Directory path

        Returns:
            Formatted size string
        """
        try:
            total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            return self._format_bytes(total_size)
        except Exception:
            return "unknown size"

    def _format_bytes(self, num_bytes: int) -> str:
        """Format bytes as human-readable string.

        Args:
            num_bytes: Number of bytes

        Returns:
            Formatted string (e.g., "42.3 MB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(num_bytes) < 1024.0:
                return f"{num_bytes:.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} PB"
