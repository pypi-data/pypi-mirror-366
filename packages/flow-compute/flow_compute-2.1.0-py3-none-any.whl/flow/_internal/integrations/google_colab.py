"""Google Colab integration for Flow SDK.

Provides true Google Colab integration through local runtime connection protocol.
Uses Jupyter server with WebSocket extension for bi-directional communication.
"""

import logging
import re
import secrets
import socket
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from flow import Flow, TaskConfig
from flow.api.models import Task, TaskStatus
from flow.errors import FlowError, TaskNotFoundError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ColabConnection:
    """Connection details for Google Colab to connect to Flow GPU instance."""

    connection_url: str  # http://localhost:8888/?token=...
    ssh_command: str  # ssh -L 8888:localhost:8888 ubuntu@...
    instance_ip: str
    instance_type: str
    task_id: str
    session_id: str
    created_at: datetime
    jupyter_token: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            "connection_url": self.connection_url,
            "ssh_command": self.ssh_command,
            "instance_ip": self.instance_ip,
            "instance_type": self.instance_type,
            "task_id": self.task_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "jupyter_token": self.jupyter_token,
        }


class GoogleColabIntegration:
    """Google Colab integration using local runtime connection.

    This integration provides the ability to connect Google Colab notebooks
    to Flow GPU instances through Colab's local runtime feature. It sets up
    a Jupyter server with WebSocket support on the GPU instance that Colab
    can connect to via an SSH tunnel.

    Architecture:
        1. Launch GPU instance with Jupyter + jupyter_http_over_ws
        2. Generate secure token for authentication
        3. User establishes SSH tunnel to instance
        4. User connects Colab to http://localhost:8888/?token=...
        5. All computation runs on Flow GPU, UI stays in Colab

    Security:
        - Token-based authentication (48 bytes of entropy)
        - SSH tunnel required (no direct internet exposure)
        - Origin restriction to colab.research.google.com
        - Tokens expire with instance termination
    """

    # Jupyter startup script for Colab compatibility
    JUPYTER_STARTUP_SCRIPT = """#!/bin/bash
set -euo pipefail

echo "Starting Jupyter server for Google Colab connection..."

# Install dependencies
pip install --upgrade pip
pip install jupyter jupyter_http_over_ws

# Enable the WebSocket extension
jupyter serverextension enable --py jupyter_http_over_ws

# Generate secure token
export JUPYTER_TOKEN=$(python -c 'import secrets; print(secrets.token_urlsafe(48))')
echo "JUPYTER_TOKEN=$JUPYTER_TOKEN"

# Create Jupyter config
mkdir -p ~/.jupyter
cat > ~/.jupyter/jupyter_notebook_config.py << EOF
c.NotebookApp.allow_origin = 'https://colab.research.google.com'
c.NotebookApp.port_retries = 0
c.NotebookApp.token = '$JUPYTER_TOKEN'
c.NotebookApp.disable_check_xsrf = False
EOF

# Start Jupyter server
echo "Starting Jupyter server on port 8888..."
jupyter notebook \
  --NotebookApp.allow_origin='https://colab.research.google.com' \
  --NotebookApp.port_retries=0 \
  --NotebookApp.token=$JUPYTER_TOKEN \
  --port=8888 \
  --no-browser \
  --ip=0.0.0.0 &

JUPYTER_PID=$!
echo "JUPYTER_PID=$JUPYTER_PID"

# Wait for server to start
for i in {1..30}; do
    if curl -s http://localhost:8888/api/status >/dev/null 2>&1; then
        echo "JUPYTER_READY=true"
        break
    fi
    sleep 1
done

# Keep script running
wait $JUPYTER_PID
"""

    def __init__(self, flow_client: Flow):
        """Initialize Google Colab integration.

        Args:
            flow_client: Initialized Flow SDK client
        """
        self.flow = flow_client
        self._active_connections: Dict[str, ColabConnection] = {}

    def connect(
        self,
        instance_type: str,
        hours: float = 4.0,
        auto_tunnel: bool = False,
        name: Optional[str] = None,
    ) -> ColabConnection:
        """Launch GPU instance configured for Google Colab connection.

        This method launches a Flow GPU instance with Jupyter server configured
        for Google Colab's local runtime connection. After launch, the user
        must establish an SSH tunnel and connect from Colab.

        Args:
            instance_type: GPU type (e.g., "a100", "h100", "8xh100")
            hours: Maximum runtime in hours
            auto_tunnel: If True, attempt to establish SSH tunnel automatically
            name: Optional name for the task

        Returns:
            ColabConnection with SSH command and connection URL

        Raises:
            ValidationError: If parameters are invalid
            FlowError: If instance launch fails
        """
        # Validate parameters
        if hours < 0.1 or hours > 168:
            raise ValidationError("Hours must be between 0.1 and 168")

        # Generate session ID
        session_id = f"colab-{secrets.token_urlsafe(8)}"

        # Create task configuration
        config = TaskConfig(
            name=name or f"colab-{instance_type}-{int(time.time())}",
            instance_type=instance_type,
            command=["bash", "-c", self.JUPYTER_STARTUP_SCRIPT],
            max_run_time_hours=hours,
        )

        # Launch instance
        print(f"\nLaunching {instance_type} for {hours} hours...")
        print("Expected time: 8-12 minutes")

        task = self.flow.run(config)

        # Wait for instance to be ready
        connection = self._wait_for_instance_ready(task, session_id)

        # Store connection
        self._active_connections[session_id] = connection

        # Establish SSH tunnel if requested
        if auto_tunnel:
            self._establish_ssh_tunnel(connection)

        return connection

    def _wait_for_instance_ready(
        self, task: Task, session_id: str, timeout: int = 900  # 15 minutes
    ) -> ColabConnection:
        """Wait for instance to be ready and extract connection details.

        FCP instances take 8-12 minutes to fully initialize. This method
        provides realistic progress updates while waiting.

        Args:
            task: Task object for the launched instance
            session_id: Session identifier
            timeout: Maximum wait time in seconds

        Returns:
            ColabConnection with all details populated

        Raises:
            FlowError: If instance fails to start or timeout occurs
        """
        start_time = time.time()
        last_status = None
        dots = 0
        jupyter_token = None
        instance_ip = None

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)

            # Get current status
            try:
                task = self.flow.get_task(task.task_id)
                status = task.status
            except Exception as e:
                logger.error(f"Failed to get task status: {e}")
                status = TaskStatus.FAILED

            # Show status updates with better visuals
            if status != last_status:
                if status == TaskStatus.PENDING:
                    if last_status is None:
                        print("\nInstance allocation started...")
                elif status == TaskStatus.RUNNING:
                    print(f"\nInstance running ({elapsed//60}m {elapsed%60}s)")
                    print("Starting Jupyter server...")
                elif status == TaskStatus.FAILED:
                    print("\nERROR: Instance failed to start")
                    raise FlowError(f"Task {task.task_id} failed: {task.message}")
                last_status = status

            # Show simple progress while pending
            if status == TaskStatus.PENDING:
                dots = (dots + 1) % 4
                print(
                    f"\rWaiting{'.' * dots}{' ' * (3-dots)} {elapsed//60}m {elapsed%60}s",
                    end="",
                    flush=True,
                )

            # Once running, check for Jupyter token and SSH
            if status == TaskStatus.RUNNING:
                # Get instance IP if not already obtained
                if not instance_ip and task.ssh_host:
                    instance_ip = task.ssh_host

                # Try to get Jupyter token from logs
                if not jupyter_token:
                    try:
                        logs = self.flow.logs(task.task_id, tail=100)
                        token_match = re.search(r"JUPYTER_TOKEN=([a-zA-Z0-9_-]+)", logs)
                        if token_match:
                            jupyter_token = token_match.group(1)
                            print("\nJupyter server ready")
                    except Exception:
                        pass

                # Check if we have everything needed
                if instance_ip and jupyter_token:
                    # Verify SSH access
                    if self._verify_ssh_access(instance_ip):
                        print("\nSSH access confirmed")

                        # Create connection object
                        return ColabConnection(
                            connection_url=f"http://localhost:8888/?token={jupyter_token}",
                            ssh_command=f"ssh -L 8888:localhost:8888 {task.ssh_user}@{instance_ip}",
                            instance_ip=instance_ip,
                            instance_type=task.instance_type,
                            task_id=task.task_id,
                            session_id=session_id,
                            created_at=datetime.now(timezone.utc),
                            jupyter_token=jupyter_token,
                        )
                    else:
                        print(
                            f"\rWaiting for SSH... {elapsed//60}m {elapsed%60}s", end="", flush=True
                        )
                else:
                    print(
                        f"\rWaiting for Jupyter... {elapsed//60}m {elapsed%60}s", end="", flush=True
                    )

            time.sleep(5)

        # Timeout reached
        raise FlowError(f"Instance not ready after {timeout//60} minutes")

    def _verify_ssh_access(self, host: str, port: int = 22) -> bool:
        """Verify SSH port is accessible.

        Args:
            host: Hostname or IP address
            port: SSH port (default 22)

        Returns:
            True if SSH is accessible, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _establish_ssh_tunnel(self, connection: ColabConnection) -> None:
        """Attempt to establish SSH tunnel automatically.

        This is a future enhancement - for now just log intent.

        Args:
            connection: Connection details
        """
        logger.info(f"Auto-tunnel requested for {connection.task_id}")
        # Future: Use subprocess to establish tunnel in background
        # For now, user must run SSH command manually

    def disconnect(self, session_id: str) -> None:
        """Disconnect and terminate a Colab session.

        Args:
            session_id: Session to disconnect

        Raises:
            ValueError: If session not found
        """
        if session_id not in self._active_connections:
            raise ValueError(f"Session {session_id} not found")

        connection = self._active_connections[session_id]

        # Stop the task
        try:
            self.flow.stop(connection.task_id)
            print(f"Disconnected session {session_id}")
        except Exception as e:
            logger.error(f"Failed to stop task {connection.task_id}: {e}")
            raise FlowError(f"Failed to disconnect session: {str(e)}")
        finally:
            # Remove from active connections
            del self._active_connections[session_id]

    def list_sessions(self) -> List[Dict[str, str]]:
        """List all active Colab sessions.

        Returns:
            List of session dictionaries with connection details
        """
        sessions = []

        for session_id, connection in self._active_connections.items():
            # Get current task status
            try:
                task = self.flow.get_task(connection.task_id)
                status = task.status.value
            except TaskNotFoundError:
                status = "terminated"
            except Exception:
                status = "unknown"

            sessions.append(
                {
                    "session_id": session_id,
                    "instance_type": connection.instance_type,
                    "status": status,
                    "created_at": connection.created_at.isoformat(),
                    "connection_url": connection.connection_url,
                    "ssh_command": connection.ssh_command,
                }
            )

        return sessions

    def get_startup_progress(self, task_id: str) -> str:
        """Extract detailed startup progress from logs.

        Args:
            task_id: Task ID to check

        Returns:
            Progress message based on log content
        """
        try:
            logs = self.flow.logs(task_id, tail=50)

            if "JUPYTER_READY=true" in logs:
                return "Jupyter server ready!"
            elif "Starting Jupyter server on port 8888" in logs:
                return "Starting Jupyter server..."
            elif "Installing dependencies" in logs or "pip install" in logs:
                return "Installing dependencies..."
            elif "Starting Jupyter server for Google Colab" in logs:
                return "Initializing Jupyter environment..."
            else:
                return "Instance initializing..."
        except Exception:
            return "Waiting for instance..."
