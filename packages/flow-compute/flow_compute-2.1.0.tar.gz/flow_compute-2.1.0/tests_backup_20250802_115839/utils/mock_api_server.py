#!/usr/bin/env python3
"""Mock API server for testing Flow CLI with various task states.

This server simulates the Flow API to test how the CLI handles different
task states, including rare ones like 'preempting'.
"""

import json
import logging
import random
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from flask import Flask, jsonify, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# In-memory task storage
tasks: Dict[str, Dict] = {}
projects: Dict[str, Dict] = {"test-project": {"name": "test-project", "region": "us-central1-b"}}


def generate_task_id() -> str:
    """Generate a task ID."""
    return f"task_{uuid4().hex[:8]}"


def generate_instance_ip() -> str:
    """Generate a random IP address."""
    return f"{random.randint(10, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"


# Predefined task scenarios - comprehensive based on FCP API spec
TASK_SCENARIOS = {
    # Normal states
    "normal_running": {
        "name": "normal-running",
        "status": "running",
        "instance_type": "H100·80G",
        "message": "Task running normally",
        "ssh_host": generate_instance_ip(),
        "ssh_port": 22,
        "cost_per_hour": "$4.50",
        "bid_status": "Allocated",
    },
    
    # Preemption states
    "preempting": {
        "name": "preempting-task",
        "status": "preempting",
        "instance_type": "H100·80G",
        "message": "Instance will be preempted in 30 seconds",
        "ssh_host": generate_instance_ip(),
        "ssh_port": 22,
        "cost_per_hour": "$4.50",
        "bid_status": "Preempting",
        "preempt_time": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
    },
    "preempted": {
        "name": "preempted-task",
        "status": "cancelled",
        "instance_type": "H100·80G", 
        "message": "Task was preempted by provider",
        "cost_per_hour": "$4.50",
        "total_cost": "$1.12",
        "bid_status": "Terminated",
        "termination_reason": "preempted",
    },
    
    # Pending/provisioning states
    "pending_long": {
        "name": "pending-forever",
        "status": "pending",
        "instance_type": "8×H100·80G",
        "message": "Waiting for 8×H100 availability (12 tasks ahead)",
        "cost_per_hour": "$36.00",
        "bid_status": "Open",
        "queue_position": 12,
    },
    "pending_capacity": {
        "name": "pending-capacity",
        "status": "pending",
        "instance_type": "4×A100·80G",
        "message": "Insufficient capacity in region us-west-2",
        "cost_per_hour": "$16.80",
        "bid_status": "Open",
        "capacity_available": 0,
        "capacity_requested": 4,
    },
    "pending_initializing": {
        "name": "pending-init",
        "status": "pending",
        "instance_type": "H100·80G",
        "message": "Instance initializing",
        "cost_per_hour": "$4.50",
        "provisioning_status": "STATUS_INITIALIZING",
        "bid_status": "Allocated",
    },
    "pending_starting": {
        "name": "pending-starting",
        "status": "pending", 
        "instance_type": "H100·80G",
        "message": "Instance starting up",
        "cost_per_hour": "$4.50",
        "provisioning_status": "STATUS_STARTING",
        "bid_status": "Allocated",
    },
    
    # Preparing states
    "preparing": {
        "name": "preparing-env",
        "status": "preparing",
        "instance_type": "H100·80G",
        "message": "Setting up environment and dependencies",
        "cost_per_hour": "$4.50",
        "provisioning_status": "STATUS_RUNNING",
        "startup_phase": "installing_dependencies",
    },
    "preparing_volumes": {
        "name": "preparing-volumes",
        "status": "preparing",
        "instance_type": "H100·80G",
        "message": "Mounting volumes and setting up storage",
        "cost_per_hour": "$4.50",
        "provisioning_status": "STATUS_RUNNING",
        "startup_phase": "mounting_volumes",
        "volumes_attached": 2,
    },
    
    # Failed states
    "failed_oom": {
        "name": "failed-oom",
        "status": "failed",
        "instance_type": "A100·40G",
        "message": "Task failed: Out of memory error",
        "cost_per_hour": "$2.10",
        "total_cost": "$0.35",
        "exit_code": 137,
        "failure_reason": "OOM_KILLED",
    },
    "failed_startup": {
        "name": "failed-startup",
        "status": "failed",
        "instance_type": "H100·80G",
        "message": "Failed to start: startup script error",
        "cost_per_hour": "$4.50",
        "total_cost": "$0.08",
        "exit_code": 1,
        "failure_reason": "STARTUP_SCRIPT_FAILED",
        "error_details": "startup.sh: line 42: command not found",
    },
    "failed_ssh_timeout": {
        "name": "failed-ssh",
        "status": "failed",
        "instance_type": "H100·80G",
        "message": "SSH connection timeout after 20 minutes",
        "cost_per_hour": "$4.50",
        "total_cost": "$1.50",
        "failure_reason": "SSH_TIMEOUT",
        "ssh_attempts": 120,
    },
    "failed_spot_reclaim": {
        "name": "failed-spot",
        "status": "failed",
        "instance_type": "H100·80G",
        "message": "Spot instance reclaimed by cloud provider",
        "cost_per_hour": "$4.50",
        "total_cost": "$3.37",
        "failure_reason": "SPOT_RECLAIMED",
    },
    
    # Completed states
    "completed_success": {
        "name": "completed-task",
        "status": "completed",
        "instance_type": "H100·80G",
        "message": "Task completed successfully",
        "cost_per_hour": "$4.50",
        "total_cost": "$18.00",
        "exit_code": 0,
    },
    "completed_with_results": {
        "name": "completed-results",
        "status": "completed",
        "instance_type": "H100·80G",
        "message": "Task completed with results available",
        "cost_per_hour": "$4.50",
        "total_cost": "$22.50",
        "exit_code": 0,
        "results_available": True,
        "results_size_mb": 1024,
    },
    
    # Cancelled states
    "cancelled_by_user": {
        "name": "cancelled-task",
        "status": "cancelled",
        "instance_type": "H100·80G",
        "message": "Cancelled by user request",
        "cost_per_hour": "$4.50",
        "total_cost": "$2.25",
        "cancellation_reason": "USER_REQUEST",
    },
    "cancelled_timeout": {
        "name": "cancelled-timeout",
        "status": "cancelled",
        "instance_type": "H100·80G",
        "message": "Cancelled: exceeded max runtime of 24 hours",
        "cost_per_hour": "$4.50",
        "total_cost": "$108.00",
        "cancellation_reason": "MAX_RUNTIME_EXCEEDED",
    },
    
    # Multi-node scenarios
    "running_multinode": {
        "name": "distributed-training",
        "status": "running",
        "instance_type": "8×H100·80G",
        "num_instances": 4,
        "message": "Distributed training across 4 nodes",
        "ssh_host": generate_instance_ip(),
        "ssh_port": 22,
        "cost_per_hour": "$144.00",
        "node_ips": [generate_instance_ip() for _ in range(4)],
        "infiniband_enabled": True,
    },
    "partial_multinode": {
        "name": "partial-nodes",
        "status": "running",
        "instance_type": "4×A100·80G",
        "num_instances": 8,
        "instances_ready": 6,
        "message": "6 of 8 nodes ready, 2 still provisioning",
        "ssh_host": generate_instance_ip(),
        "ssh_port": 22,
        "cost_per_hour": "$67.20",
    },
    
    # SSH/connectivity edge cases
    "running_no_ssh": {
        "name": "no-ssh-task",
        "status": "running",
        "instance_type": "H100·80G",
        "message": "Running (no SSH keys configured)",
        "cost_per_hour": "$4.50",
        "ssh_keys_required": False,
    },
    "running_ssh_pending": {
        "name": "ssh-pending",
        "status": "running",
        "instance_type": "H100·80G",
        "message": "SSH connection pending (network setup)",
        "cost_per_hour": "$4.50",
        "ssh_connection_status": "pending",
        "private_ip": "10.0.1.42",
    },
    "running_nat_ssh": {
        "name": "nat-ssh",
        "status": "running",
        "instance_type": "H100·80G",
        "message": "Running behind NAT gateway",
        "ssh_host": generate_instance_ip(),
        "ssh_port": 30022,  # Non-standard port
        "cost_per_hour": "$4.50",
        "nat_gateway": True,
    },
    
    # Billing/cost edge cases
    "running_free_tier": {
        "name": "free-tier",
        "status": "running",
        "instance_type": "T4·16G",
        "message": "Running on free tier allocation",
        "ssh_host": generate_instance_ip(),
        "cost_per_hour": "$0.00",
        "free_tier_hours_remaining": 8.5,
    },
    "running_discount": {
        "name": "discounted-task",
        "status": "running", 
        "instance_type": "A100·40G",
        "message": "Running with 30% partner discount",
        "ssh_host": generate_instance_ip(),
        "cost_per_hour": "$2.10",
        "discount_percentage": 30,
        "original_price": "$3.00",
    },
    
    # Error states
    "error_provisioning": {
        "name": "error-provision",
        "status": "failed",
        "instance_type": "H100·80G",
        "message": "Provisioning error: invalid image",
        "cost_per_hour": "$4.50",
        "total_cost": "$0.00",
        "provisioning_status": "STATUS_ERROR",
        "error_code": "INVALID_IMAGE",
        "error_details": "Image 'custom-image:latest' not found",
    },
    "error_validation": {
        "name": "error-validation",
        "status": "failed",
        "instance_type": "H100·80G",
        "message": "Validation error: incompatible volume type",
        "cost_per_hour": "$4.50",
        "total_cost": "$0.00",
        "validation_errors": [
            {"field": "volumes[0].interface", "message": "NVMe not supported in region"},
            {"field": "env.GPU_COUNT", "message": "Must match instance GPU count"}
        ],
    },
    
    # Paused/suspended states (mapped to pending with special message)
    "paused": {
        "name": "paused-task",
        "status": "pending",  # Maps to standard status
        "instance_type": "H100·80G",
        "message": "Task paused for maintenance",
        "cost_per_hour": "$0.00",  # Not billing while paused
        "pause_reason": "SCHEDULED_MAINTENANCE",
        "resume_eta": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
        "internal_status": "paused",  # For display purposes
    },
    
    # Relocating states (mapped to pending)
    "relocating": {
        "name": "relocating-task",
        "status": "pending",  # Maps to standard status
        "instance_type": "H100·80G",
        "message": "Migrating to different availability zone",
        "cost_per_hour": "$4.50",
        "migration_progress": 45,
        "source_zone": "us-west-2a",
        "target_zone": "us-west-2c",
        "internal_status": "relocating",
    },
    
    # Reservation/scheduled scenarios (mapped to pending)
    "scheduled_future": {
        "name": "scheduled-task",
        "status": "pending",  # Maps to standard status
        "instance_type": "8×H100·80G",
        "message": "Scheduled to start at 02:00 UTC",
        "cost_per_hour": "$36.00",
        "scheduled_start": (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat(),
        "reservation_status": "Active",
        "internal_status": "scheduled",
    },
    
    # Volume attachment scenarios
    "volume_attaching": {
        "name": "volume-attach",
        "status": "preparing",
        "instance_type": "H100·80G",
        "message": "Attaching persistent volumes (2/3 complete)",
        "cost_per_hour": "$4.50",
        "volumes_total": 3,
        "volumes_attached": 2,
        "volume_attachment_progress": 66,
    },
    
    # Kubernetes integration
    "k8s_pod_pending": {
        "name": "k8s-pending",
        "status": "pending",
        "instance_type": "H100·80G",
        "message": "Kubernetes pod scheduling",
        "cost_per_hour": "$4.50",
        "kubernetes_cluster": "prod-ml-cluster",
        "pod_status": "Pending",
        "pod_name": "flow-task-abc123",
    },
}


def create_task_from_scenario(scenario_name: str) -> Dict:
    """Create a task based on a predefined scenario."""
    scenario = TASK_SCENARIOS[scenario_name]
    task_id = generate_task_id()
    
    # Base task structure
    task = {
        "task_id": task_id,
        "name": scenario["name"],
        "status": scenario["status"],
        "instance_type": scenario["instance_type"],
        "num_instances": scenario.get("num_instances", 1),
        "region": "us-west-2",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": "user_test123",
        "cost_per_hour": scenario["cost_per_hour"],
        "message": scenario.get("message"),
        "project": "test-project",  # Add project field
    }
    
    # Add any additional fields from the scenario
    for key, value in scenario.items():
        if key not in task and key not in ["ssh_host", "ssh_port"]:
            task[key] = value
    
    # Add SSH info if running
    if scenario["status"] == "running" and "ssh_host" in scenario:
        ssh_port = scenario.get("ssh_port", 22)
        task.update({
            "ssh_host": scenario["ssh_host"],
            "ssh_port": ssh_port,
            "ssh_user": "ubuntu",
            "shell_command": f"ssh -p {ssh_port} ubuntu@{scenario['ssh_host']}",
        })
    
    # Add timestamps based on status
    if scenario["status"] in ["running", "preempting"]:
        task["started_at"] = (datetime.now(timezone.utc) - timedelta(minutes=random.randint(5, 120))).isoformat()
    elif scenario["status"] in ["completed", "failed", "cancelled"]:
        started = datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 4))
        task["started_at"] = started.isoformat()
        task["completed_at"] = (started + timedelta(hours=random.uniform(0.5, 3))).isoformat()
        task["total_cost"] = scenario.get("total_cost", f"${random.uniform(1, 50):.2f}")
    
    return task


@app.route("/api/v1/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "flow-mock-api"})


@app.route("/api/v1/auth/validate", methods=["POST"])
def validate():
    """Validate API key."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Accept any key starting with "test-"
    api_key = auth_header.replace("Bearer ", "")
    if api_key.startswith("test-"):
        return jsonify({
            "is_valid": True,
            "projects": list(projects.values()),
            "error_message": None
        })
    
    return jsonify({
        "is_valid": False,
        "projects": [],
        "error_message": "Invalid API key"
    }), 401


@app.route("/api/v1/users/<user_id>", methods=["GET"])
def get_user(user_id: str):
    """Get user information."""
    return jsonify({
        "user_id": user_id,
        "username": "testuser",
        "email": "test@example.com"
    })


@app.route("/api/v1/tasks", methods=["GET"])
def list_tasks():
    """List tasks with optional filtering."""
    status_filter = request.args.get("status")
    project_filter = request.args.get("project")
    limit = int(request.args.get("limit", 100))
    
    # Log the request for debugging
    logging.info(f"List tasks request - status: {status_filter}, project: {project_filter}, limit: {limit}")
    
    # Filter tasks
    filtered_tasks = []
    for task in tasks.values():
        # Filter by status if provided
        if status_filter and task["status"] != status_filter:
            continue
        
        # Note: In mock mode, we ignore project filter to show all tasks
        # (Real API would filter by project)
        
        filtered_tasks.append(task)
    
    # Sort by created_at desc
    filtered_tasks.sort(key=lambda t: t["created_at"], reverse=True)
    
    # Apply limit
    filtered_tasks = filtered_tasks[:limit]
    
    return jsonify({
        "tasks": filtered_tasks,
        "total": len(filtered_tasks),
        "has_more": len(filtered_tasks) >= limit
    })


@app.route("/api/v1/tasks/<task_id>", methods=["GET"])
def get_task(task_id: str):
    """Get a specific task."""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task)


@app.route("/api/v1/tasks/<task_id>/cancel", methods=["POST"])
def cancel_task(task_id: str):
    """Cancel a task."""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if task["status"] in ["completed", "failed", "cancelled"]:
        return jsonify({"error": f"Cannot cancel task in {task['status']} state"}), 400
    
    task["status"] = "cancelled"
    task["completed_at"] = datetime.now(timezone.utc).isoformat()
    task["message"] = "Cancelled by user request"
    
    return jsonify({"success": True})


@app.route("/api/v1/tasks", methods=["POST"])
def create_task():
    """Create a new task."""
    data = request.json
    scenario = data.get("scenario", "normal_running")
    
    if scenario in TASK_SCENARIOS:
        task = create_task_from_scenario(scenario)
    else:
        # Create custom task from request data
        task_id = generate_task_id()
        task = {
            "task_id": task_id,
            "name": data.get("name", f"task-{task_id[:8]}"),
            "status": data.get("status", "pending"),
            "instance_type": data.get("instance_type", "H100·80G"),
            "num_instances": data.get("num_instances", 1),
            "region": data.get("region", "us-west-2"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": "user_test123",
            "cost_per_hour": data.get("cost_per_hour", "$4.50"),
            "message": data.get("message"),
        }
    
    tasks[task["task_id"]] = task
    return jsonify(task), 201


@app.route("/api/v1/demo/create_all_scenarios", methods=["POST"])
def create_all_scenarios():
    """Create tasks for all predefined scenarios."""
    created_tasks = []
    for scenario_name in TASK_SCENARIOS:
        task = create_task_from_scenario(scenario_name)
        tasks[task["task_id"]] = task
        created_tasks.append(task)
        logging.info(f"Created {scenario_name} task: {task['task_id']}")
    
    return jsonify({
        "message": f"Created {len(created_tasks)} demo tasks",
        "tasks": created_tasks
    })


@app.route("/api/v1/demo/transition_task/<task_id>", methods=["POST"])
def transition_task(task_id: str):
    """Transition a task through different states."""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.json
    new_status = data.get("status")
    
    if new_status:
        old_status = task["status"]
        task["status"] = new_status
        
        # Update timestamps and messages based on transition
        if new_status == "running" and old_status == "pending":
            task["started_at"] = datetime.now(timezone.utc).isoformat()
            task["ssh_host"] = generate_instance_ip()
            task["ssh_port"] = 22
            task["ssh_user"] = "ubuntu"
            task["shell_command"] = f"ssh -p 22 ubuntu@{task['ssh_host']}"
            task["message"] = "Task is now running"
        elif new_status == "preempting" and old_status == "running":
            task["message"] = "Instance will be preempted in 30 seconds"
        elif new_status in ["completed", "failed", "cancelled"]:
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
            if new_status == "completed":
                task["message"] = "Task completed successfully"
            elif new_status == "failed":
                task["message"] = data.get("message", "Task failed with error")
        
        logging.info(f"Transitioned task {task_id} from {old_status} to {new_status}")
    
    return jsonify(task)


@app.route("/api/v1/demo/reset", methods=["POST"])
def reset_demo():
    """Reset all demo data."""
    tasks.clear()
    return jsonify({"message": "Demo data reset"})


if __name__ == "__main__":
    print("\n🚀 Flow Mock API Server")
    print("=" * 50)
    print("Running on: http://localhost:5555")
    print("\nEndpoints:")
    print("  - GET  /api/v1/tasks              - List all tasks")
    print("  - GET  /api/v1/tasks/<id>         - Get specific task")
    print("  - POST /api/v1/tasks              - Create task")
    print("  - POST /api/v1/tasks/<id>/cancel  - Cancel task")
    print("\nDemo endpoints:")
    print("  - POST /api/v1/demo/create_all_scenarios - Create all demo tasks")
    print("  - POST /api/v1/demo/transition_task/<id> - Change task state")
    print("  - POST /api/v1/demo/reset               - Clear all data")
    print("=" * 50)
    print()
    
    app.run(debug=True, port=5555, use_reloader=False)