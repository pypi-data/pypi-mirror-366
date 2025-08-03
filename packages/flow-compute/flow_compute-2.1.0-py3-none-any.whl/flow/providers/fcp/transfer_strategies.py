"""File transfer strategies for uploading code to FCP instances.

This module provides various strategies for transferring files to remote
instances, with rsync as the primary implementation for efficiency.
"""

import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, List, Optional, Protocol

from flow.errors import FlowError

logger = logging.getLogger(__name__)


class TransferError(FlowError):
    """Raised when file transfer fails."""

    pass


@dataclass
class TransferProgress:
    """Progress information for ongoing transfer."""

    bytes_transferred: int
    total_bytes: Optional[int]
    percentage: Optional[float]
    speed: Optional[str]  # e.g., "2.34MB/s"
    eta: Optional[str]  # e.g., "0:00:03"
    current_file: Optional[str]

    @property
    def is_complete(self) -> bool:
        """Check if transfer is complete."""
        return self.percentage is not None and self.percentage >= 100


@dataclass
class TransferResult:
    """Result of a file transfer operation."""

    success: bool
    bytes_transferred: int
    duration_seconds: float
    files_transferred: int
    error_message: Optional[str] = None

    @property
    def transfer_rate(self) -> str:
        """Calculate average transfer rate."""
        if self.duration_seconds == 0:
            return "N/A"
        rate_mbps = (self.bytes_transferred / self.duration_seconds) / (1024 * 1024)
        return f"{rate_mbps:.2f} MB/s"


class ITransferStrategy(Protocol):
    """Protocol for file transfer strategies."""

    def transfer(
        self,
        source: Path,
        target: str,
        connection: "SSHConnectionInfo",
        progress_callback: Optional[Callable[[TransferProgress], None]] = None,
    ) -> TransferResult:
        """Transfer files from source to target.

        Args:
            source: Local source directory
            target: Remote target path
            connection: SSH connection information
            progress_callback: Optional callback for progress updates

        Returns:
            TransferResult with outcome details

        Raises:
            TransferError: If transfer fails
        """
        ...


class RsyncTransferStrategy:
    """Transfer files using rsync for efficiency.

    Uses rsync for transfers with support for:
    - Compression during transfer
    - Incremental updates
    - Progress reporting
    - .flowignore exclusions
    """

    def __init__(self):
        """Initialize rsync transfer strategy."""
        self.rsync_path = self._find_rsync()

    def transfer(
        self,
        source: Path,
        target: str,
        connection: "SSHConnectionInfo",
        progress_callback: Optional[Callable[[TransferProgress], None]] = None,
    ) -> TransferResult:
        """Transfer files using rsync.

        Args:
            source: Local source directory
            target: Remote target path
            connection: SSH connection information
            progress_callback: Optional callback for progress updates

        Returns:
            TransferResult with outcome details

        Raises:
            TransferError: If rsync fails
        """
        if not source.exists():
            raise TransferError(f"Source path does not exist: {source}")

        if not source.is_dir():
            raise TransferError(f"Source must be a directory: {source}")

        # Create exclude file from .flowignore
        exclude_file = self._create_exclude_file(source)

        try:
            # Build rsync command
            cmd = self._build_rsync_command(source, target, connection, exclude_file)

            # Execute transfer
            start_time = time.time()
            result = self._execute_with_progress(cmd, progress_callback, source_path=source)
            duration = time.time() - start_time

            # Parse results
            return TransferResult(
                success=True,
                bytes_transferred=result["bytes_transferred"],
                duration_seconds=duration,
                files_transferred=result["files_transferred"],
                error_message=None,
            )

        except Exception as e:
            logger.error(f"Rsync transfer failed: {e}")
            raise TransferError(f"Transfer failed: {str(e)}") from e
        finally:
            # Clean up exclude file
            if exclude_file and exclude_file.exists():
                exclude_file.unlink()

    def _find_rsync(self) -> str:
        """Find rsync executable.

        Returns:
            Path to rsync executable

        Raises:
            TransferError: If rsync not found
        """
        try:
            result = subprocess.run(["which", "rsync"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Try common locations
        for path in ["/usr/bin/rsync", "/usr/local/bin/rsync", "/opt/homebrew/bin/rsync"]:
            if Path(path).exists():
                return path

        raise TransferError(
            "rsync not found. Please install rsync:\n"
            "  - macOS: brew install rsync\n"
            "  - Ubuntu/Debian: apt-get install rsync\n"
            "  - RHEL/CentOS: yum install rsync"
        )

    def _create_exclude_file(self, source: Path) -> Optional[Path]:
        """Create exclude file from .flowignore patterns.

        Args:
            source: Source directory

        Returns:
            Path to temporary exclude file, or None if no .flowignore
        """
        flowignore = source / ".flowignore"
        if not flowignore.exists():
            # Use default exclusions
            default_excludes = [
                ".git/",
                ".git",
                "__pycache__/",
                "*.pyc",
                ".pytest_cache/",
                ".mypy_cache/",
                ".ruff_cache/",
                ".coverage",
                "*.egg-info/",
                ".env",
                ".venv/",
                "venv/",
                "node_modules/",
                ".DS_Store",
                "*.swp",
                "*.swo",
                "*~",
                ".idea/",
                ".vscode/",
                "*.log",
            ]

            exclude_file = tempfile.NamedTemporaryFile(
                mode="w", delete=False, prefix="flow-rsync-exclude-"
            )
            exclude_file.write("\n".join(default_excludes))
            exclude_file.close()
            return Path(exclude_file.name)

        # Create temp file with .flowignore contents
        exclude_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, prefix="flow-rsync-exclude-"
        )

        with open(flowignore, "r") as f:
            # Process .flowignore patterns
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    exclude_file.write(line + "\n")

        exclude_file.close()
        return Path(exclude_file.name)

    def _build_rsync_command(
        self,
        source: Path,
        target: str,
        connection: "SSHConnectionInfo",
        exclude_file: Optional[Path],
    ) -> List[str]:
        """Build rsync command with appropriate flags.

        Args:
            source: Local source directory
            target: Remote target path
            connection: SSH connection details
            exclude_file: Optional path to exclude file

        Returns:
            List of command arguments
        """
        # SSH command for rsync
        ssh_cmd = (
            f"ssh -p {connection.port} "
            f"-i {connection.key_path} "
            f"-o StrictHostKeyChecking=no "
            f"-o UserKnownHostsFile=/dev/null "
            f"-o ConnectTimeout=10 "
            f"-o ServerAliveInterval=10 "
            f"-o ServerAliveCountMax=3"
        )

        cmd = [
            self.rsync_path,
            "-avz",  # archive, verbose, compress
            "--progress",  # Show progress
            "--human-readable",  # Human-readable sizes
            "--stats",  # Show statistics
            "--partial",  # Keep partial files for resume
            "--partial-dir=.rsync-partial",  # Store partials in hidden dir
            "--timeout=30",  # I/O timeout for network issues
            "--contimeout=10",  # Connection timeout
            "-e",
            ssh_cmd,  # Use custom SSH command
        ]

        # Add exclude file if present
        if exclude_file:
            cmd.extend(["--exclude-from", str(exclude_file)])

        # Add source and destination
        # Trailing slash on source to copy contents, not directory itself
        cmd.append(f"{source}/")
        cmd.append(f"{connection.destination}:{target}/")

        return cmd

    def _execute_with_progress(
        self, cmd: List[str], progress_callback: Optional[Callable[[TransferProgress], None]], 
        source_path: Optional[Path] = None
    ) -> dict:
        """Execute rsync with progress monitoring.

        Args:
            cmd: Rsync command to execute
            progress_callback: Optional progress callback
            source_path: Source directory path for calculating statistics

        Returns:
            Dictionary with transfer statistics

        Raises:
            TransferError: If rsync fails
        """
        logger.debug(f"Executing rsync: {' '.join(cmd[:3])}...")

        # Track statistics
        bytes_transferred = 0
        files_transferred = 0
        current_file = None

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )

            # Process output line by line
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue

                # Parse progress updates
                progress = self._parse_rsync_progress(line)
                if progress and progress_callback:
                    if progress.current_file:
                        current_file = progress.current_file
                    progress_callback(progress)

                # Track statistics
                if "Number of files transferred:" in line:
                    match = re.search(r"(\d+)", line)
                    if match:
                        files_transferred = int(match.group(1))

                elif "Total transferred file size:" in line:
                    # Parse size (can be in various units)
                    match = re.search(r"([\d,]+)", line)
                    if match:
                        bytes_transferred = int(match.group(1).replace(",", ""))

            # Wait for completion
            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                raise TransferError(f"rsync failed with code {process.returncode}: {stderr}")

            # If we didn't capture statistics from output, estimate
            if bytes_transferred == 0 and source_path:
                # Rough estimate based on source size
                if source_path.exists():
                    bytes_transferred = sum(f.stat().st_size for f in source_path.rglob("*") if f.is_file())

            return {"bytes_transferred": bytes_transferred, "files_transferred": files_transferred}

        except subprocess.SubprocessError as e:
            raise TransferError(f"Failed to execute rsync: {e}") from e

    def _parse_rsync_progress(self, line: str) -> Optional[TransferProgress]:
        """Parse rsync progress output.

        Args:
            line: Line of rsync output

        Returns:
            TransferProgress if this is a progress line, None otherwise
        """
        # Progress line format:
        # "32,768,000  78%    2.34MB/s    0:00:03"
        progress_match = re.match(r"\s*([\d,]+)\s+(\d+)%\s+([\d.]+\w+/s)\s+([\d:]+)", line)

        if progress_match:
            bytes_transferred = int(progress_match.group(1).replace(",", ""))
            percentage = float(progress_match.group(2))
            speed = progress_match.group(3)
            eta = progress_match.group(4)

            # Calculate total from percentage
            total_bytes = None
            if percentage > 0:
                total_bytes = int(bytes_transferred * 100 / percentage)

            return TransferProgress(
                bytes_transferred=bytes_transferred,
                total_bytes=total_bytes,
                percentage=percentage,
                speed=speed,
                eta=eta,
                current_file=None,
            )

        # Summary line format:
        # "xfr#1, to-chk=0/1"
        summary_match = re.search(r"xfr#(\d+)", line)
        if summary_match:
            # This indicates completion
            return TransferProgress(
                bytes_transferred=0,
                total_bytes=None,
                percentage=100.0,
                speed=None,
                eta="0:00:00",
                current_file=None,
            )

        # File transfer line: Check if this is a filename
        # Skip lines that are clearly not filenames
        if line and not any(line.startswith(prefix) for prefix in [
            "building", "sending", "sent", "total", "created", "deleting", 
            "Number of", "Total", "Matched", "File list", "sent ", "total size"
        ]):
            # Check if it doesn't have progress indicators
            if "%" not in line and "/s" not in line:
                # This is likely a filename
                return TransferProgress(
                    bytes_transferred=0,
                    total_bytes=None,
                    percentage=None,
                    speed=None,
                    eta=None,
                    current_file=line.strip(),
                )

        return None


# Add time import that was missing
import time
