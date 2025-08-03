"""Health check command for diagnosing Flow SDK issues.

This command provides comprehensive diagnostics for common Flow SDK problems
including connectivity, authentication, state synchronization, and instance health.
"""

import json
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flow import Flow
from flow.api.health_models import (
    FleetHealthSummary,
    GPUMetric,
    HealthStatus,
    NodeHealthSnapshot,
    SystemMetrics,
)
from flow.api.models import TaskStatus, InstanceStatus
from flow.cli.utils.animated_progress import AnimatedEllipsisProgress
from flow.cli.utils.health_renderer import HealthRenderer
from flow.health.gpu_health_checker import (
    GPUdStatus,
    GPUdStatusDiagnoser,
    NodeHealthSnapshotFactory,
    HealthCheckMessageHandler,
    SSHConnectionHandler,
    GPUInstanceDetector,
    TaskAgeCalculator,
)
from flow.health.storage import MetricsAggregator, MetricsStore
from flow.providers.fcp.ssh_utils import SSHTunnelManager

from .base import BaseCommand

console = Console()


class HealthChecker:
    """Performs comprehensive health checks on Flow SDK setup."""

    def __init__(self, flow_client: Flow):
        self.flow_client = flow_client
        self.issues = []
        self.warnings = []
        self.successes = []
        self.renderer = HealthRenderer()
        self.metrics_store = MetricsStore()
        self.gpud_diagnoser = GPUdStatusDiagnoser()
        self.snapshot_factory = NodeHealthSnapshotFactory()
        self.message_handler = HealthCheckMessageHandler(self.issues, self.warnings, self.successes)
        self.gpu_detector = GPUInstanceDetector()
        self.age_calculator = TaskAgeCalculator()

    def add_issue(self, category: str, message: str, suggestion: str = None):
        """Add a critical issue."""
        self.issues.append({"category": category, "message": message, "suggestion": suggestion})

    def add_warning(self, category: str, message: str, suggestion: str = None):
        """Add a warning."""
        self.warnings.append({"category": category, "message": message, "suggestion": suggestion})

    def add_success(self, category: str, message: str):
        """Add a success."""
        self.successes.append({"category": category, "message": message})

    def check_connectivity(self) -> bool:
        """Check API connectivity."""
        try:
            # Try a simple API call to verify connectivity
            # Use list_tasks with limit=1 as a lightweight connectivity check
            self.flow_client.list_tasks(limit=1)
            self.add_success("Connectivity", "Successfully connected to Flow API")
            return True
        except Exception as e:
            self.add_issue(
                "Connectivity",
                f"Cannot connect to Flow API: {str(e)}",
                "Check your internet connection and API endpoint configuration",
            )
            return False

    def check_authentication(self) -> bool:
        """Check authentication status."""
        try:
            # Get current config
            config = self.flow_client.config
            if config and config.provider_config:
                project = config.provider_config.get('project', 'unknown')
                region = config.provider_config.get('region', 'unknown')
                if project != 'unknown':
                    self.add_success(
                        "Authentication",
                        f"Authenticated to project '{project}' in region '{region}'",
                    )
                    return True
                else:
                    self.add_issue(
                        "Authentication",
                        "No project configured",
                        "Run 'flow init' to configure project",
                    )
                    return False
            else:
                self.add_issue(
                    "Authentication",
                    "No authentication configured",
                    "Run 'flow init' to configure authentication",
                )
                return False
        except Exception as e:
            self.add_issue(
                "Authentication",
                f"Authentication error: {str(e)}",
                "Run 'flow init' to reconfigure authentication",
            )
            return False

    def check_ssh_keys(self) -> bool:
        """Check SSH key configuration."""
        try:
            config_path = Path.home() / ".flow" / "config.yaml"
            if not config_path.exists():
                self.add_issue(
                    "SSH Keys",
                    "Flow configuration file not found",
                    "Run 'flow init' to set up Flow SDK",
                )
                return False

            # Read config to check SSH keys
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)

            ssh_key_path = config.get("ssh_key_path")
            if not ssh_key_path:
                self.add_warning(
                    "SSH Keys",
                    "No SSH key path configured",
                    "SSH keys will be auto-generated when needed",
                )
            else:
                # Expand path and check if it exists
                key_path = Path(ssh_key_path).expanduser()
                if key_path.exists():
                    self.add_success("SSH Keys", f"SSH key found at {key_path}")
                else:
                    self.add_issue(
                        "SSH Keys",
                        f"SSH key not found at {key_path}",
                        "Generate a new SSH key or update the path in ~/.flow/config.yaml",
                    )
                    return False

            return True
        except Exception as e:
            self.add_warning(
                "SSH Keys",
                f"Could not check SSH keys: {str(e)}",
                "SSH functionality may be limited",
            )
            return True

    def check_instance_sync(self) -> dict[str, list[dict]]:
        """Check for state synchronization issues between Flow and provider.
        
        Uses the same TaskFetcher as 'flow status' for consistency.
        Early returns on provider connectivity issues to avoid false positives.
        """
        # Use the same task fetcher as status command for consistency
        from flow.cli.utils.task_fetcher import TaskFetcher
        fetcher = TaskFetcher(self.flow_client)
        
        # Get active tasks using proven logic from status command
        active_tasks = [
            task for task in fetcher.fetch_all_tasks(limit=100, prioritize_active=True)
            if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]
        ]
        
        # Early return if no active tasks
        if not active_tasks:
            self.add_success("State Sync", "No active tasks to synchronize")
            return {"flow_tasks": [], "provider_instances": [], "orphaned": [], "missing": []}
        
        # Build Flow task list
        flow_task_map = {
            task.task_id: {
                "id": task.task_id,
                "name": task.name,
                "status": task.status.value if hasattr(task.status, 'value') else str(task.status)
            }
            for task in active_tasks
        }
        
        # Get provider state - fail fast if provider is unreachable
        provider_task_ids = self._get_provider_task_ids()
        if provider_task_ids is None:
            # Provider unreachable - return early to avoid false "missing" reports
            return {
                "flow_tasks": list(flow_task_map.values()),
                "provider_instances": [],
                "orphaned": [],
                "missing": []
            }
        
        # Find discrepancies
        missing = [
            task_data for task_id, task_data in flow_task_map.items()
            if task_id not in provider_task_ids
        ]
        
        # Report results
        if missing:
            self.add_issue(
                "State Sync",
                f"Found {len(missing)} tasks missing from provider",
                "These tasks are tracked by Flow but don't exist in the provider. Try 'flow status --force-refresh'.",
            )
        else:
            self.add_success(
                "State Sync",
                f"State is synchronized: {len(active_tasks)} active tasks",
            )
        
        return {
            "flow_tasks": list(flow_task_map.values()),
            "provider_instances": [{"task_id": tid} for tid in provider_task_ids],
            "orphaned": [],  # Could be extended to check for orphaned provider tasks
            "missing": missing
        }
    
    def _get_provider_task_ids(self) -> set[str] | None:
        """Get task IDs from provider, returns None if provider unreachable.
        
        This is a focused method that just gets task IDs, making it easy to test
        and reason about. Returns None to signal provider connectivity issues.
        """
        try:
            provider = self.flow_client._ensure_provider()
            task_ids = set()
            
            # Fetch both running and pending tasks
            for status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
                try:
                    tasks = provider.list_tasks(status=status, limit=100)
                    task_ids.update(task.task_id for task in tasks)
                except Exception as e:
                    # Log but continue - partial data is better than none
                    self.add_warning(
                        "State Sync",
                        f"Could not list {status.value} tasks from provider: {str(e)}",
                    )
            
            # If we got no tasks at all, assume provider is unreachable
            if not task_ids:
                self.add_issue(
                    "State Sync",
                    "Could not retrieve any tasks from provider",
                    "Provider may be unreachable or authentication may have failed. Check provider connectivity.",
                )
                return None
                
            return task_ids
            
        except Exception as e:
            self.add_issue(
                "State Sync",
                f"Failed to connect to provider: {str(e)}",
                "Check your provider configuration and network connectivity.",
            )
            return None

    def check_instance_health(self, task_id: str) -> dict[str, any]:
        """Check health of a specific instance."""
        health = {
            "task_id": task_id,
            "reachable": False,
            "ssh_ready": False,
            "age_hours": None,
            "issues": [],
        }

        try:
            task = self.flow_client.get_task(task_id)

            # Calculate age
            if task.created_at:
                age = datetime.now(timezone.utc) - task.created_at
                health["age_hours"] = age.total_seconds() / 3600

            # Check if we have SSH info
            if not task.ssh_host:
                health["issues"].append("No SSH host assigned")
                return health

            # Check network reachability
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "2", task.ssh_host], capture_output=True, timeout=3
                )
                health["reachable"] = result.returncode == 0
            except Exception:
                health["issues"].append("Cannot check network reachability")

            # Check SSH readiness
            if health["reachable"]:
                try:
                    # Quick SSH test
                    ssh_test = subprocess.run(
                        [
                            "ssh",
                            "-o",
                            "ConnectTimeout=5",
                            "-o",
                            "StrictHostKeyChecking=no",
                            "-o",
                            "UserKnownHostsFile=/dev/null",
                            "-o",
                            "PasswordAuthentication=no",
                            "-o",
                            "BatchMode=yes",
                            f"{task.ssh_user}@{task.ssh_host}",
                            "echo",
                            "OK",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )

                    if ssh_test.returncode == 0:
                        health["ssh_ready"] = True
                    else:
                        stderr = ssh_test.stderr.lower()
                        if "connection reset" in stderr or "kex_exchange" in stderr:
                            health["issues"].append("SSH service is still starting up")
                        elif "connection refused" in stderr:
                            health["issues"].append("SSH port is closed")
                        elif "permission denied" in stderr:
                            health["issues"].append("SSH authentication failed")
                        else:
                            health["issues"].append(f"SSH test failed: {ssh_test.stderr.strip()}")
                except subprocess.TimeoutExpired:
                    health["issues"].append("SSH connection timed out")
                except Exception as e:
                    health["issues"].append(f"SSH test error: {str(e)}")

        except Exception as e:
            health["issues"].append(f"Could not fetch task details: {str(e)}")

        return health

    def check_gpu_health(self, task_id: str) -> NodeHealthSnapshot | None:
        """Check GPU health for a specific task using GPUd API.

        Args:
            task_id: Task ID to check

        Returns:
            NodeHealthSnapshot if successful, None otherwise
        """
        try:
            task = self.flow_client.get_task(task_id)

            # Skip non-GPU instances
            if not self.gpu_detector.is_gpu_instance(task.instance_type):
                self.add_warning("GPU Health", f"Task {task_id} is not using a GPU instance type")
                return None

            # Calculate task age
            task_age_hours = self.age_calculator.get_age_hours(task.created_at)

            # Default GPUd port
            gpud_port = 15132

            # Use SSHTunnelManager with context manager for automatic cleanup
            try:
                # Try a quick SSH connectivity check first (optional marker check)
                marker_status = None
                try:
                    ssh_prefix = self._build_ssh_command_prefix(task)
                    marker_status = self.gpud_diagnoser.check_gpud_marker(ssh_prefix)
                except Exception:
                    # Skip marker check if SSH is problematic
                    pass
                
                # Add timeout protection for SSH tunnel
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("SSH tunnel creation timed out")
                
                # Set alarm for tunnel creation (10 seconds max)
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)
                
                try:
                    with SSHTunnelManager.tunnel_context(
                        task=task,
                        remote_port=gpud_port,
                        local_port=0,  # Auto-allocate local port
                    ) as tunnel:
                        # Cancel alarm once tunnel is established
                        signal.alarm(0)
                        
                        api_url = f"http://localhost:{tunnel.local_port}"
                        
                        # Diagnose GPUd status with marker info
                        diagnosis = self._diagnose_with_marker(api_url, task_age_hours, marker_status)
                finally:
                    # Restore signal handler and cancel any pending alarm
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                    
                    # Handle diagnosis result
                    self.message_handler.handle_diagnosis(diagnosis, task_id)
                    
                    # Create appropriate snapshot based on diagnosis
                    if diagnosis.status == GPUdStatus.LEGACY:
                        return self.snapshot_factory.create_legacy_snapshot(task)
                    elif diagnosis.status == GPUdStatus.NOT_INSTALLED:
                        return self.snapshot_factory.create_not_installed_snapshot(task)
                    elif diagnosis.status == GPUdStatus.FAILED:
                        return self.snapshot_factory.create_failed_snapshot(task, diagnosis.reason)
                    elif diagnosis.status == GPUdStatus.STARTING:
                        return self.snapshot_factory.create_starting_snapshot(task)
                    elif diagnosis.status == GPUdStatus.HEALTHY:
                        # GPUd is healthy - proceed with full health check
                        snapshot = self._query_gpud_api(api_url, task)
                        if snapshot:
                            self.metrics_store.write_snapshot(snapshot)
                            self._analyze_gpu_health(snapshot)
                        return snapshot
                    else:
                        # Should not reach here, but handle gracefully
                        return self.snapshot_factory.create_failed_snapshot(task, "Unknown GPUd status")

            except TimeoutError as e:
                # SSH tunnel timed out
                self.add_warning(
                    "GPU Health",
                    f"SSH connection to {task_id} timed out",
                    "Node may be unreachable or under heavy load"
                )
                return self.snapshot_factory.create_unreachable_snapshot(task, "SSH connection timeout")
            except Exception as e:
                # SSH connection failed - analyze the error
                ssh_diagnosis = SSHConnectionHandler.analyze_ssh_error(e, task_age_hours)
                self.message_handler.handle_diagnosis(ssh_diagnosis, task_id)
                
                # Create appropriate snapshot
                if ssh_diagnosis.status == GPUdStatus.LEGACY:
                    return self.snapshot_factory.create_legacy_snapshot(task)
                else:
                    return self.snapshot_factory.create_unreachable_snapshot(task, ssh_diagnosis.reason)

        except Exception as e:
            self.add_issue("GPU Health", f"Failed to check GPU health: {str(e)}")
            return None
    
    def _build_ssh_command_prefix(self, task: Any) -> list[str]:
        """Build SSH command prefix for remote commands."""
        import os
        from pathlib import Path
        import yaml
        
        cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "PasswordAuthentication=no",
            "-o", "ConnectTimeout=5",
        ]
        
        # Add port if non-standard
        if task.ssh_port and task.ssh_port != 22:
            cmd.extend(["-p", str(task.ssh_port)])
        
        # Add SSH key if configured (same logic as SSHTunnelManager)
        ssh_key = os.environ.get("FLOW_SSH_KEY_PATH")
        if not ssh_key:
            try:
                config_path = Path.home() / ".flow" / "config.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        ssh_key = config.get("ssh_key_path")
            except Exception:
                pass
        
        if ssh_key:
            ssh_key = os.path.expanduser(ssh_key)
            if os.path.exists(ssh_key):
                cmd.extend(["-i", ssh_key])
        
        # Add destination
        cmd.append(f"{task.ssh_user}@{task.ssh_host}")
        
        return cmd
    
    def _diagnose_with_marker(self, api_url: str, task_age_hours: float | None, marker_status: str | None) -> Any:
        """Diagnose GPUd status using both API check and marker file."""
        from flow.health.gpu_health_checker import GPUdDiagnosis, GPUdStatus
        
        # If marker shows GPUd was attempted but failed, it's a real failure
        if marker_status in ["install_failed", "start_failed", "not_ready"]:
            return GPUdDiagnosis(
                GPUdStatus.FAILED,
                f"GPUd setup was attempted but failed: {marker_status}",
                {"marker_status": marker_status}
            )
        
        # If marker shows running, defer to API check
        if marker_status == "running":
            return self.gpud_diagnoser.diagnose(api_url, task_age_hours)
        
        # If no marker (None), GPUd was never attempted
        if marker_status is None:
            # Could be legacy or manual start
            if task_age_hours and task_age_hours > 24:
                return GPUdDiagnosis(
                    GPUdStatus.LEGACY,
                    "Task started before GPU monitoring was available"
                )
            else:
                return GPUdDiagnosis(
                    GPUdStatus.NOT_INSTALLED,
                    "GPUd not installed (instance started without Flow startup script)"
                )
        
        # Default to standard diagnosis
        return self.gpud_diagnoser.diagnose(api_url, task_age_hours)


    def _query_gpud_api(self, api_url: str, task: Any) -> NodeHealthSnapshot | None:
        """Query GPUd API endpoints to build health snapshot.

        Args:
            api_url: GPUd API base URL
            task: Task object with instance info

        Returns:
            NodeHealthSnapshot if successful
        """
        try:
            # Check if GPUd is running
            try:
                health_resp = requests.get(f"{api_url}/health", timeout=5)
                gpud_healthy = health_resp.status_code == 200
            except Exception:
                gpud_healthy = False

            if not gpud_healthy:
                self.add_issue("GPU Health", "GPUd is not responding", "Check if GPUd is running on the instance")
                return None

            # Get machine info
            machine_info = {}
            try:
                resp = requests.get(f"{api_url}/machine-info", timeout=5)
                if resp.status_code == 200:
                    machine_info = resp.json()
            except Exception:
                pass

            # Get GPU metrics
            gpu_metrics = []
            try:
                resp = requests.get(f"{api_url}/v1/gpu", timeout=5)
                if resp.status_code == 200:
                    gpu_data = resp.json()
                    # Convert to our GPUMetric format
                    for idx, gpu in enumerate(gpu_data.get("gpus", [])):
                        metric = GPUMetric(
                            gpu_index=idx,
                            uuid=gpu.get("uuid", ""),
                            name=gpu.get("product_name", "Unknown"),
                            temperature_c=gpu.get("temperature", {}).get("current", 0),
                            power_draw_w=gpu.get("power", {}).get("draw", 0),
                            power_limit_w=gpu.get("power", {}).get("limit", 0),
                            memory_used_mb=gpu.get("memory", {}).get("used", 0) // (1024 * 1024),
                            memory_total_mb=gpu.get("memory", {}).get("total", 0) // (1024 * 1024),
                            gpu_utilization_pct=gpu.get("utilization", {}).get("gpu", 0),
                            sm_occupancy_pct=gpu.get("utilization", {}).get("encoder", 0),
                            clock_mhz=gpu.get("clocks", {}).get("current", {}).get("graphics", 0),
                            max_clock_mhz=gpu.get("clocks", {}).get("max", {}).get("graphics", 0),
                        )
                        gpu_metrics.append(metric)
            except Exception as e:
                self.add_warning("GPU Health", f"Failed to get GPU metrics: {str(e)}")

            # Get system metrics
            system_metrics = None
            try:
                resp = requests.get(f"{api_url}/v1/cpu", timeout=5)
                if resp.status_code == 200:
                    cpu_data = resp.json()
                    system_metrics = SystemMetrics(
                        cpu_usage_pct=cpu_data.get("usage_percent", 0),
                        memory_used_gb=cpu_data.get("memory", {}).get("used_gb", 0),
                        memory_total_gb=cpu_data.get("memory", {}).get("total_gb", 0),
                        disk_usage_pct=0,  # Not provided by GPUd
                        load_average=cpu_data.get("load_average", []),
                    )
            except Exception:
                pass

            # Create snapshot
            snapshot = NodeHealthSnapshot(
                task_id=task.task_id,
                task_name=task.name or task.task_id,
                instance_id=getattr(task, "instance_id", "unknown"),
                instance_type=task.instance_type or "unknown",
                timestamp=datetime.now(timezone.utc),
                gpud_healthy=gpud_healthy,
                gpud_version=machine_info.get("gpud_version"),
                machine_info=machine_info,
                gpu_metrics=gpu_metrics,
                system_metrics=system_metrics,
            )

            # Calculate health score
            snapshot.health_score = self._calculate_health_score(snapshot)
            snapshot.health_status = self._determine_health_status(snapshot.health_score)

            return snapshot

        except Exception as e:
            self.add_issue("GPU Health", f"Failed to query GPUd API: {str(e)}")
            return None

    def _calculate_health_score(self, snapshot: NodeHealthSnapshot) -> float:
        """Calculate overall health score from metrics.

        Args:
            snapshot: Node health snapshot

        Returns:
            Health score between 0.0 and 1.0
        """
        if not snapshot.gpu_metrics:
            return 0.5  # No GPU data

        scores = []

        for gpu in snapshot.gpu_metrics:
            gpu_score = 1.0

            # Temperature (0-100°C, critical at 85°C)
            if gpu.temperature_c >= 85:
                gpu_score *= 0.5
            elif gpu.temperature_c >= 75:
                gpu_score *= 0.8

            # GPU utilization (penalize if too low or consistently maxed)
            if gpu.gpu_utilization_pct < 10:
                gpu_score *= 0.9  # Underutilized
            elif gpu.gpu_utilization_pct >= 95:
                gpu_score *= 0.95  # Possibly bottlenecked

            # Memory pressure
            if gpu.memory_utilization_pct >= 95:
                gpu_score *= 0.8
            elif gpu.memory_utilization_pct >= 90:
                gpu_score *= 0.9

            # Power throttling
            if gpu.is_throttling:
                gpu_score *= 0.7

            # ECC errors
            if gpu.ecc_errors > 0:
                gpu_score *= 0.6

            scores.append(gpu_score)

        # System metrics impact
        if snapshot.system_metrics:
            sys_score = 1.0
            if snapshot.system_metrics.cpu_usage_pct >= 95:
                sys_score *= 0.9
            if snapshot.system_metrics.memory_utilization_pct >= 95:
                sys_score *= 0.8
            scores.append(sys_score)

        # Average all scores
        return sum(scores) / len(scores) if scores else 0.5

    def _determine_health_status(self, score: float) -> HealthStatus:
        """Determine health status from score."""
        if score >= 0.8:
            return HealthStatus.HEALTHY
        elif score >= 0.6:
            return HealthStatus.DEGRADED
        elif score > 0:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.UNKNOWN

    def _analyze_gpu_health(self, snapshot: NodeHealthSnapshot) -> None:
        """Analyze GPU health and add appropriate issues/warnings."""
        if not snapshot.gpu_metrics:
            return

        for gpu in snapshot.gpu_metrics:
            # Temperature warnings
            if gpu.temperature_c >= 85:
                self.add_issue(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} temperature critical: {gpu.temperature_c}°C",
                    "Check cooling and reduce workload"
                )
            elif gpu.temperature_c >= 75:
                self.add_warning(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} temperature high: {gpu.temperature_c}°C"
                )

            # Memory pressure
            if gpu.memory_utilization_pct >= 95:
                self.add_warning(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} memory nearly full: {gpu.memory_utilization_pct:.0f}%",
                    "Consider using gradient checkpointing or smaller batch sizes"
                )

            # Throttling
            if gpu.is_throttling:
                self.add_issue(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} is throttling (clock: {gpu.clock_mhz}MHz, max: {gpu.max_clock_mhz}MHz)",
                    "Check power limits and thermal conditions"
                )

            # ECC errors
            if gpu.ecc_errors > 0:
                self.add_issue(
                    "GPU Health",
                    f"GPU {gpu.gpu_index} has {gpu.ecc_errors} ECC errors",
                    "Monitor for increasing errors; may indicate hardware issues"
                )

        # Overall status
        if snapshot.health_status == HealthStatus.HEALTHY:
            self.add_success("GPU Health", f"All {len(snapshot.gpu_metrics)} GPUs are healthy")

    def check_fleet_gpu_health(self, show_all: bool = False, json_mode: bool = False) -> FleetHealthSummary:
        """Check GPU health across all running tasks.

        Args:
            show_all: Include non-GPU tasks
            json_mode: Skip animations if True

        Returns:
            Fleet health summary
        """
        # Get running tasks
        tasks = self.flow_client.list_tasks(status=TaskStatus.RUNNING, limit=100)

        if not show_all:
            # Filter GPU tasks using the detector
            tasks = [t for t in tasks if self.gpu_detector.is_gpu_instance(t.instance_type)]

        if not tasks:
            if not json_mode:
                console.print("[yellow]No GPU tasks are currently running[/yellow]")
            self.add_warning("GPU Health", "No GPU tasks are currently running")
            return FleetHealthSummary(
                timestamp=datetime.now(timezone.utc),
                total_nodes=0,
                healthy_nodes=0,
                degraded_nodes=0,
                critical_nodes=0,
                total_gpus=0,
                healthy_gpus=0,
                avg_gpu_temperature=0,
                avg_gpu_utilization=0,
                avg_gpu_memory_utilization=0,
            )

        # Collect health snapshots with or without animation
        snapshots = []
        if json_mode:
            # No animation in JSON mode
            for task in tasks:
                snapshot = self.check_gpu_health(task.task_id)
                if snapshot:
                    snapshots.append(snapshot)
                time.sleep(0.1)  # Rate limiting
        else:
            # Show progress animation
            with AnimatedEllipsisProgress(console, f"Checking health of {len(tasks)} tasks") as progress:
                for i, task in enumerate(tasks):
                    progress.update_message(f"Checking {task.name or task.task_id} ({i+1}/{len(tasks)})")
                    snapshot = self.check_gpu_health(task.task_id)
                    if snapshot:
                        snapshots.append(snapshot)
                    time.sleep(0.1)  # Rate limiting

        # Calculate summary
        return self._calculate_fleet_summary(snapshots)

    def _calculate_fleet_summary(self, snapshots: list[NodeHealthSnapshot]) -> FleetHealthSummary:
        """Calculate fleet-wide health summary from snapshots.

        Args:
            snapshots: List of node health snapshots

        Returns:
            Fleet health summary
        """
        # Separate different types of nodes
        monitored_snapshots = [s for s in snapshots if s.health_status != HealthStatus.UNKNOWN]
        unmonitored_snapshots = [s for s in snapshots if s.health_status == HealthStatus.UNKNOWN]
        
        # Further categorize unmonitored nodes
        legacy_snapshots = [s for s in unmonitored_snapshots 
                           if "legacy" in s.machine_info.get("note", "").lower()]
        not_installed_snapshots = [s for s in unmonitored_snapshots 
                                  if "not installed" in s.machine_info.get("note", "").lower()]
        
        # Count nodes by status (excluding unmonitored)
        total_nodes = len(monitored_snapshots)
        healthy_nodes = sum(1 for s in monitored_snapshots if s.health_status == HealthStatus.HEALTHY)
        degraded_nodes = sum(1 for s in monitored_snapshots if s.health_status == HealthStatus.DEGRADED)
        critical_nodes = sum(1 for s in monitored_snapshots if s.health_status == HealthStatus.CRITICAL)

        # GPU metrics (only from monitored tasks)
        all_gpus = [gpu for s in monitored_snapshots for gpu in s.gpu_metrics]
        total_gpus = len(all_gpus)
        healthy_gpus = sum(1 for gpu in all_gpus if gpu.temperature_c < 75 and not gpu.is_throttling)

        # Averages (only from monitored tasks)
        avg_temp = sum(gpu.temperature_c for gpu in all_gpus) / total_gpus if total_gpus > 0 else 0
        avg_util = sum(gpu.gpu_utilization_pct for gpu in all_gpus) / total_gpus if total_gpus > 0 else 0
        avg_mem = sum(gpu.memory_utilization_pct for gpu in all_gpus) / total_gpus if total_gpus > 0 else 0

        # Collect critical issues
        critical_issues = []
        warnings = []

        for snapshot in snapshots:
            if snapshot.health_status == HealthStatus.CRITICAL:
                for issue in self.issues:
                    if issue["category"] == "GPU Health":
                        critical_issues.append({
                            "task_name": snapshot.task_name,
                            "component": "GPU",
                            "message": issue["message"],
                        })

            for gpu in snapshot.gpu_metrics:
                if gpu.temperature_c >= 85:
                    critical_issues.append({
                        "task_name": snapshot.task_name,
                        "component": f"GPU {gpu.gpu_index}",
                        "message": f"Critical temperature: {gpu.temperature_c}°C",
                    })
                elif gpu.temperature_c >= 75:
                    warnings.append({
                        "task_name": snapshot.task_name,
                        "component": f"GPU {gpu.gpu_index}",
                        "message": f"High temperature: {gpu.temperature_c}°C",
                    })

        # Add notes about unmonitored tasks
        if legacy_snapshots:
            warnings.append({
                "task_name": "Legacy Tasks",
                "component": "GPU Monitoring",
                "message": f"{len(legacy_snapshots)} task(s) started before GPU monitoring was available",
            })
        
        if not_installed_snapshots:
            warnings.insert(0, {
                "task_name": "Manual Tasks",
                "component": "GPU Monitoring", 
                "message": f"{len(not_installed_snapshots)} task(s) without GPU monitoring (started manually or via console)",
            })
        
        return FleetHealthSummary(
            timestamp=datetime.now(timezone.utc),
            total_nodes=total_nodes,
            healthy_nodes=healthy_nodes,
            degraded_nodes=degraded_nodes,
            critical_nodes=critical_nodes,
            total_gpus=total_gpus,
            healthy_gpus=healthy_gpus,
            avg_gpu_temperature=avg_temp,
            avg_gpu_utilization=avg_util,
            avg_gpu_memory_utilization=avg_mem,
            critical_issues=critical_issues[:10],  # Limit to 10
            warnings=warnings[:10],  # Limit to 10
            legacy_nodes=len(legacy_snapshots),  # Track legacy nodes
        )

    def generate_report(self) -> dict[str, any]:
        """Generate comprehensive health report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "issues": len(self.issues),
                "warnings": len(self.warnings),
                "successes": len(self.successes),
            },
            "details": {
                "issues": self.issues,
                "warnings": self.warnings,
                "successes": self.successes,
            },
        }


class HealthCommand(BaseCommand):
    """Health check command implementation."""

    @property
    def name(self) -> str:
        return "health"

    @property
    def help(self) -> str:
        return """Run comprehensive health checks on Flow SDK setup - Diagnose connectivity, auth, and GPU issues

Quick diagnostics:
  flow health                      # Check SDK connectivity and config
  flow health --task my-job        # Diagnose specific task issues
  flow health --gpu                # Monitor GPU health for all tasks
  
Advanced usage:
  flow health --fix                # Auto-fix common configuration issues
  flow health --task job-123 --history 24  # View 24-hour health history
  flow health --json               # Machine-readable output for automation"""

    def get_command(self) -> click.Command:
        @click.command(name=self.name, help=self.help)
        @click.option("--json", is_flag=True, help="Output results as JSON")
        @click.option("--fix", is_flag=True, help="Attempt to fix issues automatically")
        @click.option("--task", help="Check health of specific task")
        @click.option("--gpu", is_flag=True, help="Check GPU health for all GPU tasks")
        @click.option("--all", "show_all", is_flag=True, help="Include all tasks (not just GPU tasks) when using --gpu")
        @click.option("--history", type=int, help="Show health history for last N hours (requires --task)")
        @click.option("--verbose", "-v", is_flag=True, help="Show detailed diagnostics and explanations")
        def health(json: bool, fix: bool, task: str | None, gpu: bool, show_all: bool, history: int | None, verbose: bool):
            """Run health checks on Flow SDK setup.

            \b
            Examples:
                flow health                 # Check connectivity and auth
                flow health --fix           # Auto-fix common issues
                flow health --task my-job   # Diagnose specific task
                flow health --gpu           # Monitor GPU health
                flow health --json          # Machine-readable output

            Use 'flow health --verbose' for detailed diagnostics and troubleshooting.
            """
            if verbose and not any([json, fix, task, gpu]):
                console.print("\n[bold]Flow Health Check Details:[/bold]\n")
                console.print("What it checks:")
                console.print("  • API connectivity and response times")
                console.print("  • Authentication and credential validity")
                console.print("  • SSH key configuration and access")
                console.print("  • Running instance synchronization")
                console.print("  • GPU health metrics (temperature, memory, utilization)")
                console.print("  • Task state consistency\n")
                
                console.print("Common issues and fixes:")
                console.print("  • Missing credentials → flow init")
                console.print("  • SSH key problems → flow ssh-keys add ~/.ssh/id_rsa.pub")
                console.print("  • Stale instance state → flow health --fix")
                console.print("  • GPU thermal throttling → Check cooling/reduce load")
                console.print("  • Network issues → Check firewall/VPN settings\n")
                
                console.print("Advanced options:")
                console.print("  flow health --task job-123 --history 24  # 24-hour health history")
                console.print("  flow health --gpu --all                  # All tasks, not just GPU")
                console.print("  flow health --fix --json                 # Automated repair with JSON output\n")
                return
                
            self._execute(json, fix, task, gpu, show_all, history, verbose)

        return health

    def _execute(self, output_json: bool, fix: bool, task_id: str | None, gpu: bool, show_all: bool, history: int | None, verbose: bool = False) -> None:
        """Execute health check command."""
        try:
            flow_client = Flow()
            checker = HealthChecker(flow_client)

            # GPU health check mode
            if gpu:
                # Check fleet GPU health (has its own animation)
                fleet_summary = checker.check_fleet_gpu_health(show_all=show_all, json_mode=output_json)

                # Display summary
                if not output_json:
                    checker.renderer.render_fleet_summary(fleet_summary)

                    # Show individual node health
                    if fleet_summary.total_nodes > 0:
                        console.print("\n")
                        # Get snapshots from recent checks
                        snapshots = list(checker.metrics_store.read_snapshots(
                            start_date=datetime.now(timezone.utc) - timedelta(minutes=5)
                        ))
                        if snapshots:
                            checker.renderer.render_node_health_table(
                                snapshots,
                                title="GPU Node Health Status"
                            )

                # Generate report
                report = checker.generate_report()
                report["fleet_summary"] = {
                    "timestamp": fleet_summary.timestamp.isoformat(),
                    "total_nodes": fleet_summary.total_nodes,
                    "healthy_nodes": fleet_summary.healthy_nodes,
                    "degraded_nodes": fleet_summary.degraded_nodes,
                    "critical_nodes": fleet_summary.critical_nodes,
                    "total_gpus": fleet_summary.total_gpus,
                    "healthy_gpus": fleet_summary.healthy_gpus,
                    "avg_gpu_temperature": fleet_summary.avg_gpu_temperature,
                    "avg_gpu_utilization": fleet_summary.avg_gpu_utilization,
                    "avg_gpu_memory_utilization": fleet_summary.avg_gpu_memory_utilization,
                    "critical_issues": fleet_summary.critical_issues,
                    "warnings": fleet_summary.warnings,
                }

                if output_json:
                    print(json.dumps(report, indent=2))

                return

            # Task health history mode
            if task_id and history:
                if not output_json:
                    with AnimatedEllipsisProgress(
                        console, f"Loading health history for {task_id}", start_immediately=True
                    ) as progress:
                        # Read historical snapshots
                        snapshots = list(checker.metrics_store.read_snapshots(
                            start_date=datetime.now(timezone.utc) - timedelta(hours=history),
                            task_id=task_id
                        ))
                else:
                    # JSON mode - no animation
                    snapshots = list(checker.metrics_store.read_snapshots(
                        start_date=datetime.now(timezone.utc) - timedelta(hours=history),
                        task_id=task_id
                    ))

                if snapshots:
                    # Get latest snapshot for detailed view
                    latest = max(snapshots, key=lambda s: s.timestamp)

                    if not output_json:
                        checker.renderer.render_node_details(latest)

                        # Show history summary
                        if len(snapshots) > 1:
                            aggregator = MetricsAggregator(checker.metrics_store)
                            summary = aggregator.get_task_summary(task_id, history)

                            console.print("\n[bold]Historical Summary[/bold]")
                            console.print(f"Snapshots: {summary['snapshot_count']}")
                            console.print(f"Average Health Score: {summary['health_score']['average']:.1%}")
                            console.print(f"Min/Max: {summary['health_score']['min']:.1%} / {summary['health_score']['max']:.1%}")
                            console.print(f"Unhealthy Periods: {summary['unhealthy_periods']}")
                    else:
                        report = {
                            "task_id": task_id,
                            "hours": history,
                            "snapshots": [s.to_dict() for s in snapshots],
                            "latest": latest.to_dict(),
                        }
                        print(json.dumps(report, indent=2))
                else:
                    if not output_json:
                        console.print(f"[yellow]No health history found for task {task_id}[/yellow]")
                    else:
                        print(json.dumps({"error": f"No health history found for task {task_id}"}, indent=2))

                return

            # Regular health check mode
            if not output_json:
                # Use animated progress for all health checks
                with AnimatedEllipsisProgress(
                    console, "Running Flow SDK Health Checks", start_immediately=True
                ) as progress:
                    # 1. Connectivity check
                    progress.base_message = "Checking connectivity"
                    checker.check_connectivity()

                    # 2. Authentication check
                    progress.base_message = "Checking authentication"
                    checker.check_authentication()

                    # 3. SSH keys check
                    progress.base_message = "Checking SSH keys"
                    checker.check_ssh_keys()

                    # 4. Instance sync check
                    progress.base_message = "Checking state synchronization"
                    sync_status = checker.check_instance_sync()
            else:
                # JSON mode - no progress indicator
                # 1. Connectivity check
                checker.check_connectivity()

                # 2. Authentication check
                checker.check_authentication()

                # 3. SSH keys check
                checker.check_ssh_keys()

                # 4. Instance sync check
                sync_status = checker.check_instance_sync()

            # 5. Specific task check if requested
            task_health = None
            gpu_health = None
            if task_id:
                task_health = checker.check_instance_health(task_id)

                # Add task-specific findings
                if task_health["ssh_ready"]:
                    checker.add_success("Task Health", f"Task {task_id} is healthy and SSH-ready")
                else:
                    issues_str = (
                        ", ".join(task_health["issues"]) if task_health["issues"] else "Unknown"
                    )
                    checker.add_issue(
                        "Task Health",
                        f"Task {task_id} has issues: {issues_str}",
                        "Check logs with 'flow logs' or try restarting the task",
                    )

                # Also check GPU health for this task
                gpu_health = checker.check_gpu_health(task_id)
                if gpu_health and not output_json:
                    console.print("\n")
                    checker.renderer.render_node_details(gpu_health)

            # Generate report
            report = checker.generate_report()
            report["sync_status"] = sync_status
            if task_health:
                report["task_health"] = task_health

            # Output results
            if output_json:
                print(json.dumps(report, indent=2))
            else:
                self._display_report(report, fix)

        except Exception as e:
            if output_json:
                error_report = {
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                print(json.dumps(error_report, indent=2))
            else:
                console.print(f"[red]✗ Health check failed: {str(e)}[/red]")

    def _display_report(self, report: dict, fix: bool) -> None:
        """Display health check report in human-readable format."""
        summary = report["summary"]
        details = report["details"]

        # Summary panel
        status = "🟢 Healthy" if summary["issues"] == 0 else "🔴 Issues Found"
        summary_text = f"{status}\n\n"
        summary_text += f"✓ {summary['successes']} checks passed\n"
        if summary["warnings"] > 0:
            summary_text += f"⚠ {summary['warnings']} warnings\n"
        if summary["issues"] > 0:
            summary_text += f"✗ {summary['issues']} issues found\n"

        console.print(Panel(summary_text, title="Health Check Summary"))

        # Successes
        if details["successes"]:
            console.print("\n[green]✓ Passed Checks:[/green]")
            for success in details["successes"]:
                console.print(f"  • {success['category']}: {success['message']}")

        # Warnings
        if details["warnings"]:
            console.print("\n[yellow]⚠ Warnings:[/yellow]")
            for warning in details["warnings"]:
                console.print(f"  • {warning['category']}: {warning['message']}")
                if warning.get("suggestion"):
                    console.print(f"    → {warning['suggestion']}")

        # Issues
        if details["issues"]:
            console.print("\n[red]✗ Issues Found:[/red]")
            for issue in details["issues"]:
                console.print(f"  • {issue['category']}: {issue['message']}")
                if issue.get("suggestion"):
                    console.print(f"    → {issue['suggestion']}")

        # Sync status details
        if "sync_status" in report:
            sync = report["sync_status"]
            if sync["orphaned"]:
                console.print("\n[yellow]Orphaned Instances:[/yellow]")
                table = Table(show_header=True)
                table.add_column("Instance ID")
                table.add_column("Task ID")
                table.add_column("Status")
                table.add_column("Created")

                for inst in sync["orphaned"]:
                    table.add_row(
                        inst["id"][:12] if inst["id"] else "-",
                        inst.get("task_id", "")[:12] if inst.get("task_id") else "-",
                        inst["status"],
                        inst.get("created", "Unknown"),
                    )
                console.print(table)

                if fix:
                    console.print("\n[yellow]To terminate orphaned instances:[/yellow]")
                    console.print("  Visit https://console.mlfoundry.com/instances")
                    console.print("  Or contact FCP support for assistance")

        # Task health details
        if "task_health" in report:
            health = report["task_health"]
            console.print(f"\n[bold]Task Health: {health['task_id']}[/bold]")
            console.print(f"  • Network Reachable: {'✓' if health['reachable'] else '✗'}")
            console.print(f"  • SSH Ready: {'✓' if health['ssh_ready'] else '✗'}")
            if health["age_hours"]:
                console.print(f"  • Age: {health['age_hours']:.1f} hours")
            if health["issues"]:
                console.print("  • Issues:")
                for issue in health["issues"]:
                    console.print(f"    - {issue}")

        # Next steps
        console.print("\n[bold]Next Steps:[/bold]")
        if summary["issues"] > 0:
            console.print("  • Review and address the issues listed above")
            console.print("  • Run 'flow health --fix' to attempt automatic fixes")
            console.print("  • Check logs with 'flow logs <task-name>' for more details")
        else:
            console.print("  • Your Flow SDK setup is healthy!")
            console.print("  • Run 'flow status' to see your tasks")
            console.print("  • Submit new tasks with 'flow run'")


# Export command instance
command = HealthCommand()
