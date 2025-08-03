"""Test data generators for Flow SDK tests."""

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal

from flow.api.models import TaskConfig, TaskStatus


class TestDataGenerator:
    """Generate realistic test data programmatically."""

    @staticmethod
    def generate_task_config(
        complexity: Literal["minimal", "standard", "complex"] = "standard",
        num_instances: int = 1,
        with_volumes: bool = False,
        with_env: bool = False
    ) -> TaskConfig:
        """Generate test task configurations.
        
        Args:
            complexity: Level of configuration complexity
            num_instances: Number of instances
            with_volumes: Include volume configuration
            with_env: Include environment variables
            
        Returns:
            TaskConfig object for testing
        """
        base_config = {
            "name": f"test-task-{TestDataGenerator._random_id(6)}",
            "instance_type": "a100.80gb.sxm4.1x",
            "num_instances": num_instances
        }

        if complexity == "minimal":
            base_config["command"] = "echo 'Hello World'"

        elif complexity == "standard":
            base_config.update({
                "command": "python train.py --epochs 10",
                "working_dir": "/workspace",
                "max_runtime_hours": 2
            })

        elif complexity == "complex":
            base_config.update({
                "command": "bash train.sh",
                "working_dir": "/workspace",
                "max_runtime_hours": 24,
                "script": """#!/bin/bash
                    pip install -r requirements.txt
                    python setup.py
                """,
                "shutdown_script": "python cleanup.py",
                "persistent_home": True
            })

        if with_volumes:
            base_config["volumes"] = [
                {
                    "size_gb": 100,
                    "mount_path": "/data"
                },
                {
                    "volume_id": "vol-existing-123",
                    "mount_path": "/models"
                }
            ]

        if with_env:
            base_config["env"] = {
                "CUDA_VISIBLE_DEVICES": "0,1",
                "WANDB_API_KEY": "test-key-123",
                "MODEL_PATH": "/models/latest"
            }

        return TaskConfig(**base_config)

    @staticmethod
    def generate_api_response(
        endpoint: str,
        scenario: Literal["success", "error", "timeout", "quota_exceeded"] = "success",
        version: str = "v2024-01-01"
    ) -> Dict[str, Any]:
        """Generate mock API responses.
        
        Args:
            endpoint: API endpoint name
            scenario: Response scenario to generate
            version: API version for compatibility
            
        Returns:
            Mock API response dictionary
        """
        if scenario == "error":
            return {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "request_id": TestDataGenerator._random_id(16)
                }
            }

        if scenario == "timeout":
            # This would be handled by the mock raising a timeout exception
            return None

        if scenario == "quota_exceeded":
            return {
                "error": {
                    "code": "QUOTA_EXCEEDED",
                    "message": "Monthly GPU quota exceeded",
                    "details": {
                        "quota_hours": 100,
                        "used_hours": 100.5,
                        "requested_hours": 2
                    }
                }
            }

        # Success responses by endpoint
        responses = {
            "submit_task": {
                "bid_id": f"bid-{TestDataGenerator._random_id(8)}",
                "status": "pending",
                "estimated_start_time": TestDataGenerator._future_timestamp(minutes=5),
                "message": "Task submitted successfully"
            },
            "get_bid": {
                "bid_id": f"bid-{TestDataGenerator._random_id(8)}",
                "status": random.choice(["pending", "scheduled", "running", "completed"]),
                "instance_type": "a100.80gb.sxm4.1x",
                "ssh_host": f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "ssh_port": 22,
                "ssh_user": "ubuntu",
                "start_time": TestDataGenerator._past_timestamp(hours=1),
                "cost_per_hour": 25.60,
                "total_cost": 12.80
            },
            "list_bids": {
                "bids": [
                    TestDataGenerator.generate_api_response("get_bid")
                    for _ in range(random.randint(1, 5))
                ],
                "total": random.randint(5, 50),
                "page": 1,
                "per_page": 20
            },
            "create_volume": {
                "volume_id": f"vol-{TestDataGenerator._random_id(8)}",
                "size_gb": 100,
                "status": "available",
                "created_at": TestDataGenerator._past_timestamp(minutes=1)
            },
            "list_volumes": {
                "volumes": [
                    {
                        "volume_id": f"vol-{TestDataGenerator._random_id(8)}",
                        "name": f"data-{i}",
                        "size_gb": random.choice([50, 100, 200, 500]),
                        "status": "available",
                        "created_at": TestDataGenerator._past_timestamp(days=i)
                    }
                    for i in range(3)
                ]
            }
        }

        return responses.get(endpoint, {"status": "ok"})

    @staticmethod
    def generate_task_status_sequence(
        final_status: TaskStatus = TaskStatus.COMPLETED,
        include_timestamps: bool = True
    ) -> List[Dict[str, Any]]:
        """Generate a realistic sequence of task status updates.
        
        Args:
            final_status: The final status the task should reach
            include_timestamps: Whether to include timestamp fields
            
        Returns:
            List of status update dictionaries
        """
        sequence = []
        base_time = datetime.now(timezone.utc) - timedelta(hours=1)

        # Always start with pending
        statuses = [TaskStatus.PENDING]

        if final_status != TaskStatus.PENDING:
            statuses.append(TaskStatus.SCHEDULED)

        if final_status in [TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED]:
            statuses.append(TaskStatus.RUNNING)

        if final_status != TaskStatus.RUNNING:
            statuses.append(final_status)

        for i, status in enumerate(statuses):
            update = {
                "status": status.value,
                "message": TestDataGenerator._status_message(status)
            }

            if include_timestamps:
                update["timestamp"] = (base_time + timedelta(minutes=i*5)).isoformat()

            if status == TaskStatus.RUNNING:
                update["ssh_host"] = "10.0.1.100"
                update["ssh_port"] = 22

            if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                update["total_cost"] = 25.60 * (i * 0.1)  # Rough cost calculation

            sequence.append(update)

        return sequence

    @staticmethod
    def generate_log_output(
        log_type: Literal["training", "error", "system"] = "training",
        lines: int = 10
    ) -> str:
        """Generate realistic log output for testing.
        
        Args:
            log_type: Type of logs to generate
            lines: Number of log lines
            
        Returns:
            Multi-line log string
        """
        log_lines = []

        if log_type == "training":
            for i in range(lines):
                log_lines.append(
                    f"[2024-01-01 12:{i:02d}:00] Epoch {i+1}/10 - "
                    f"loss: {random.uniform(0.1, 0.9):.4f} - "
                    f"accuracy: {random.uniform(0.8, 0.99):.4f}"
                )

        elif log_type == "error":
            errors = [
                "CUDA out of memory. Tried to allocate 2.00 GiB",
                "RuntimeError: Expected all tensors to be on the same device",
                "ValueError: Expected input batch_size (32) to match target batch_size (64)",
                "FileNotFoundError: [Errno 2] No such file or directory: '/data/train.csv'"
            ]
            for i in range(min(lines, len(errors))):
                log_lines.append(f"[ERROR] {errors[i]}")

        elif log_type == "system":
            log_lines = [
                "Starting task execution...",
                "Checking GPU availability...",
                "Found 1 GPU: NVIDIA H100 80GB HBM3",
                "Loading dataset from /data/dataset.tar.gz",
                "Dataset loaded: 50000 training samples, 10000 validation samples",
                "Initializing model...",
                "Model initialized with 1.5B parameters",
                "Starting training loop..."
            ][:lines]

        return "\n".join(log_lines)

    @staticmethod
    def _random_id(length: int = 8) -> str:
        """Generate random ID string."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    @staticmethod
    def _future_timestamp(minutes: int = 5) -> str:
        """Generate ISO timestamp in the future."""
        return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat() + "Z"

    @staticmethod
    def _past_timestamp(minutes: int = 0, hours: int = 0, days: int = 0) -> str:
        """Generate ISO timestamp in the past."""
        delta = timedelta(minutes=minutes, hours=hours, days=days)
        return (datetime.now(timezone.utc) - delta).isoformat() + "Z"

    @staticmethod
    def _status_message(status: TaskStatus) -> str:
        """Generate appropriate message for status."""
        messages = {
            TaskStatus.PENDING: "Task submitted and awaiting resources",
            TaskStatus.SCHEDULED: "Resources allocated, preparing to start",
            TaskStatus.RUNNING: "Task is running on GPU instance",
            TaskStatus.COMPLETED: "Task completed successfully",
            TaskStatus.FAILED: "Task failed with error",
            TaskStatus.CANCELLED: "Task was cancelled by user"
        }
        return messages.get(status, "Unknown status")
