# Flow CLI Mock API Testing System

This mock system allows you to test how the Flow CLI responds to various API states, including rare and edge case scenarios that are difficult to reproduce in production.

## Overview

The mock system consists of:
1. **Mock API Server** (`mock_api_server.py`) - Flask server that simulates the Flow API
2. **Mock Configuration** (`mock_flow_config.yaml`) - Points Flow CLI to the mock server
3. **Test Script** (`test_cli_states.py`) - Demonstrates various scenarios

## Quick Start

### 1. Start the Mock API Server

In one terminal:
```bash
cd tests
python mock_api_server.py
```

The server runs on http://localhost:5555

### 2. Run the Test Script

In another terminal:
```bash
cd tests
python test_cli_states.py
```

This will:
- Set up the environment to use the mock API
- Create demo tasks with various states
- Demonstrate how the CLI displays each state

### 3. Manual Testing

To manually test with the mock API:
```bash
# Set the config file
export FLOW_CONFIG_FILE=tests/mock_flow_config.yaml

# Now use flow commands normally
flow status
flow status --status preempting
flow status failed-oom
```

## Available Task States

The mock server provides comprehensive scenarios based on the FCP API:

### Standard States
- `pending` - Task waiting for resources
- `running` - Task actively executing
- `preempting` - Task will be terminated soon (rare)
- `completed` - Task finished successfully
- `failed` - Task terminated with error
- `cancelled` - Task cancelled by user

### Provisioning States
- `pending-init` - Instance initializing
- `pending-starting` - Instance starting up
- `preparing-env` - Setting up environment
- `preparing-volumes` - Mounting volumes

### Failure Scenarios
- `failed-oom` - Out of memory error
- `failed-startup` - Startup script failed
- `failed-ssh` - SSH timeout
- `failed-spot` - Spot instance reclaimed

### Multi-node Scenarios
- `distributed-training` - 4 nodes running
- `partial-nodes` - 6 of 8 nodes ready

### SSH/Connectivity Edge Cases
- `no-ssh-task` - Running without SSH keys
- `ssh-pending` - SSH pending network setup
- `nat-ssh` - Behind NAT with non-standard port

### Billing Scenarios
- `free-tier` - Running on free allocation
- `discounted-task` - With partner discount

### Special States
- `paused-task` - Paused for maintenance
- `relocating-task` - Migrating zones
- `scheduled-task` - Future scheduled
- `k8s-pending` - Kubernetes pod scheduling

## API Endpoints

### Standard Endpoints
- `GET /api/v1/tasks` - List all tasks
- `GET /api/v1/tasks/<id>` - Get specific task
- `POST /api/v1/tasks` - Create custom task
- `POST /api/v1/tasks/<id>/cancel` - Cancel task

### Demo Endpoints
- `POST /api/v1/demo/create_all_scenarios` - Create all demo tasks
- `POST /api/v1/demo/transition_task/<id>` - Change task state
- `POST /api/v1/demo/reset` - Clear all data

## Creating Custom Scenarios

### Via API
```python
import requests

# Create a custom task
response = requests.post(
    "http://localhost:5000/api/v1/tasks",
    json={
        "name": "custom-task",
        "status": "running",
        "instance_type": "H100·80G",
        "message": "Custom message",
        "ssh_host": "10.0.0.1",
        "cost_per_hour": "$4.50",
        "bid_status": "Allocated",
        "custom_field": "any_value"
    },
    headers={"Authorization": "Bearer test-mock-api-key"}
)
```

### Transition States
```python
# Transition a task through states
task_id = "task_abc123"

# Pending → Running
requests.post(
    f"http://localhost:5000/api/v1/demo/transition_task/{task_id}",
    json={"status": "running"},
    headers={"Authorization": "Bearer test-mock-api-key"}
)

# Running → Preempting
requests.post(
    f"http://localhost:5000/api/v1/demo/transition_task/{task_id}",
    json={"status": "preempting"},
    headers={"Authorization": "Bearer test-mock-api-key"}
)
```

## Testing Specific Scenarios

### Preemption Flow
```bash
# See preempting tasks
flow status --status preempting

# Watch a specific preempting task
flow status preempting-task
```

### Cost Analysis
```bash
# Get JSON output for analysis
flow status --all --json | python -m json.tool

# Filter high-cost tasks
flow status --all | grep "144.00"  # 8×H100 tasks
```

### SSH Issues
```bash
# Tasks without SSH
flow status no-ssh-task

# Tasks with pending SSH
flow status ssh-pending
```

### Failed Tasks
```bash
# All failed tasks
flow status --status failed

# Specific failure
flow status failed-oom
```

## Advanced Usage

### Continuous Monitoring
```bash
# Watch status updates
watch -n 2 'FLOW_CONFIG_FILE=tests/mock_flow_config.yaml flow status'

# Monitor preempting tasks
watch -n 1 'FLOW_CONFIG_FILE=tests/mock_flow_config.yaml flow status --status preempting'
```

### Scripting
```python
#!/usr/bin/env python3
import os
import subprocess
import json

# Use mock API
os.environ["FLOW_CONFIG_FILE"] = "tests/mock_flow_config.yaml"

# Get all tasks as JSON
result = subprocess.run(
    ["flow", "status", "--all", "--json"],
    capture_output=True,
    text=True
)

tasks = json.loads(result.stdout)["tasks"]

# Analyze states
state_counts = {}
for task in tasks:
    state = task["status"]
    state_counts[state] = state_counts.get(state, 0) + 1

print("Task state distribution:", state_counts)
```

## Troubleshooting

### Server Not Starting
- Check if port 5555 is already in use
- Install Flask: `pip install flask`
- Note: Port 5000 is often used by AirPlay on macOS, so we use 5555 instead

### CLI Not Using Mock API
- Verify FLOW_CONFIG_FILE is set correctly
- Check mock_flow_config.yaml path
- Ensure api_url points to localhost:5555

### Authentication Errors
- Mock server accepts any key starting with "test-"
- Default key in config: `test-mock-api-key`

## Extending the Mock System

To add new scenarios:

1. Add to TASK_SCENARIOS in mock_api_server.py:
```python
"new_scenario": {
    "name": "new-scenario-name",
    "status": "running",  # Must be valid TaskStatus
    "instance_type": "H100·80G",
    "message": "Description",
    # Add any fields the CLI might display
}
```

2. Recreate demo tasks:
```bash
curl -X POST http://localhost:5000/api/v1/demo/reset
curl -X POST http://localhost:5000/api/v1/demo/create_all_scenarios
```

3. Test the new scenario:
```bash
flow status new-scenario-name
```

## Notes

- The mock server stores all data in memory (resets on restart)
- All timestamps are generated dynamically
- IP addresses are randomly generated
- The mock API is intentionally permissive for testing