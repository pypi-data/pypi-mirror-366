# Flow SDK

[![PyPI](https://img.shields.io/pypi/v/flow-compute.svg)](https://pypi.org/project/flow-compute/)
[![Python](https://img.shields.io/pypi/pyversions/flow-compute.svg)](https://pypi.org/project/flow-compute/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE.txt)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/foundrytechnologies/flow-v2)

**GPU compute in seconds, not hours** — Flow SDK provides seamless access to GPU infrastructure with a single, simple API. The Flow system is tailored for launching and orchestrating batch tasks and experiments. 

## Table of Contents

- [Quick Start](#quick-start)
- [Overview](#overview)
- [Installation](#installation)
- [Authentication](#authentication)
- [Basic Usage](#basic-usage)
- [Development Environment](#development-environment)
- [Guide for SLURM Users](#guide-for-slurm-users)
- [Instance Types](#instance-types)
- [Task Management](#task-management)
- [Persistent Storage](#persistent-storage)
- [Zero-Import Remote Execution](#zero-import-remote-execution)
- [Decorator Pattern](#decorator-pattern)
- [Data Mounting](#data-mounting)
- [Multi-Node Training](#multi-node-training)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Common Patterns](#common-patterns)
- [Performance](#performance)
- [Support](#support)
- [License](#license)

## Quick Start

**Prerequisites:** Get your API key at [app.mlfoundry.com](https://app.mlfoundry.com/account/apikeys)

### 1. Install and Configure

```bash
# Install Flow SDK (handles Python version automatically)
uv tool install flow-compute

# Configure your API key
flow init  # One-time setup wizard
```

### 2. Run on GPU

**Option A: Development Environment (Recommended)**
```bash
# Start a persistent dev VM with container-based execution
flow dev

# Run commands in isolated containers
flow dev -c 'python train.py'
```

**Option B: Direct Instance Launch**
```bash
# Launch an interactive GPU instance in seconds
flow run --instance-type h100

# SSH into it when ready
flow ssh <task-id>
```

**Option C: Submit a Script**
```python
import flow

# Your code launches in the background, and will be running on an instance in minutes
task = flow.run("python train.py", instance_type="h100x8")
```

That's it. Your local `train.py` file and project files are automatically uploaded and running on an H100 node.

**Note:** Your code is uploaded, but you need to install dependencies. See [Handling Dependencies](#handling-dependencies).

## Why Flow

Long-standing AI research labs have invested to build sophisticated infrastructure abstractions that enable researchers to focus on research rather than DevOps. DeepMind's Xmanager handles experiments from single GPUs to hundreds of hosts. Meta's submitit brings Python-native patterns to cluster computing. OpenAI's internal platform was designed to seamlessly scale from interactive notebooks to thousand-GPU training runs.

Flow brings these same capabilities to every AI developer. Like these internal tools, Flow provides:
- **Progressive disclosure** - Simple tasks stay simple, complex workflows remain possible
- **Unified abstraction** - One interface whether running locally or across heterogenous cloud hardware  
- **Fail-fast validation** - Catch configuration errors before expensive compute starts
- **Experiment tracking** - Built-in task history and reproducibility

The goal: democratize the infrastructure abstractions that enable breakthrough AI research.

## Overview

Flow SDK provides a high-level interface for GPU workload submission across heterogeneous infrastructure. Our design philosophy emphasizes explicit behavior, progressive disclosure, and fail-fast validation.

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────┐
│   Your Code │  -->  │   Flow SDK   │  -->  │   Cloud Infra   │
│ train.py    │       │ Unified API  │       │ FCP, ... others │
└─────────────┘       └──────────────┘       └─────────────────┘
     Local               client-side          cloud accelerators 
```

### Core Capabilities

- **Unified API**: Single interface across cloud providers (FCP, AWS, GCP, Azure)
- **Zero DevOps**: Automatic instance provisioning, driver setup, and environment configuration
- **Cost Control**: Built-in safeguards with max price and runtime limits
- **Persistent Storage**: Volumes that persist across task lifecycles
- **Multi-Node**: Native support for distributed training
- **Real-Time Monitoring**: Log streaming, SSH access, and status tracking
- **Notebook Integration**: Google Colab and Jupyter notebook support

## Installation

### Quick Install (Recommended)

**One-line install:**
```bash
curl -sSL https://raw.githubusercontent.com/foundrytechnologies/flow-sdk/main/setup.sh | bash
```

**Or manually:**
```bash
# Install uv if needed (automatically handles Python versions)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Flow SDK
uv tool install flow-sdk

# Start using Flow
flow init
```

That's it! Flow is now available globally in your terminal.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/foundrytechnologies/flow-sdk
cd flow-sdk

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"

# Verify
flow --version
```

### Alternative: pip install
```bash
# Requires Python 3.10+ already installed
pip install flow-sdk
```

## Authentication

Run the interactive setup wizard:

```bash
flow init
```

This will:
1. Prompt for your API key (get one at [app.mlfoundry.com](https://app.mlfoundry.com))
2. Help you select a project
3. Configure SSH keys (optional)
4. Enable shell completion automatically
5. Save settings for all Flow tools

Alternative methods:

**Environment Variables**
```bash
export FCP_API_KEY="fcp-..."
export FCP_PROJECT="my-project"
```

**Manual Config File**
```yaml
# ~/.flow/config.yaml
api_key: fcp-...
project: my-project
region: us-central1-b
```

**Verify Setup**
```bash
flow status
# Should show "No tasks found" if authenticated
```

## Basic Usage

### Python API

```python
import flow
from flow import TaskConfig

# Simple GPU job - automatically uploads your local code
task = flow.run("python train.py", instance_type="a100")

# Wait for completion
task.wait()
print(task.logs())

# Full configuration
config = TaskConfig(
    name="distributed-training",
    instance_type="8xa100",  # 8x A100 GPUs
    command=["python", "-m", "torch.distributed.launch", 
             "--nproc_per_node=8", "train.py"],
    volumes=[{"size_gb": 100, "mount_path": "/data"}],
    max_price_per_hour=25.0,  # Cost protection
    max_run_time_hours=24.0   # Time limit
)
task = flow.run(config)

# Monitor execution
print(f"Status: {task.status}")
print(f"Shell: {task.shell_command}")
print(f"Cost: {task.cost_per_hour}")
```

### Code Upload

By default, Flow automatically uploads your current directory to the GPU instance:

```python
# This uploads your local files and runs them on GPU
task = flow.run("python train.py", instance_type="a100")

# Disable code upload (use pre-built Docker image)
task = flow.run(
    "python /app/train.py",
    instance_type="a100",
    image="mycompany/training:latest",
    upload_code=False
)
```

Use `.flowignore` file to exclude files from upload (same syntax as `.gitignore`).

### Handling Dependencies

Your code is uploaded, but dependencies need to be installed:

```python
# Install dependencies from pyproject.toml
task = flow.run(
    "pip install . && python train.py",
    instance_type="a100"
)

# Using uv (recommended for speed)
task = flow.run(
    "uv pip install . && python train.py",
    instance_type="a100"
)

# Pre-installed in Docker image (fastest)
task = flow.run(
    "python train.py",
    instance_type="a100",
    image="pytorch/pytorch:2.0.0-cuda11.8-cudnn8"  # PyTorch pre-installed
)

# Using private ECR images (auto-authenticates with AWS credentials)
task = flow.run(
    "python train.py",
    instance_type="a100",
    image="123456789.dkr.ecr.us-east-1.amazonaws.com/my-ml-image:latest",
    env={
        "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
        "AWS_SECRET_ACCESS_KEY": os.environ["AWS_SECRET_ACCESS_KEY"],
    }
)
```

### Command Line

```bash
# Quick interactive GPU instance
flow run --instance-type h100              # Launch H100 instance
flow run -i 8xa100                         # 8x A100 GPUs
flow run -i 4xa100                         # 4x A100 GPUs
flow run -i h100 --name dev-box           # Named instance

# Submit tasks from config
flow run config.yaml                       # From YAML file
flow run job.yaml --watch                  # Watch progress

# Monitor tasks
flow status                                # List all tasks
flow logs task-abc123 -f                   # Stream logs
flow ssh task-abc123                       # SSH access

# Manage tasks
flow cancel task-abc123                    # Stop execution
flow cancel --name-pattern "dev-*"         # Cancel all tasks starting with "dev-"
flow cancel -n "flow-dev-*" --yes          # Cancel matching tasks without confirmation
```

### YAML Configuration

```yaml
# config.yaml
name: model-training
instance_type: 4xa100
command: python train.py --epochs 100
env:
  BATCH_SIZE: "256"
  LEARNING_RATE: "0.001"
volumes:
  - size_gb: 500
    mount_path: /data
    name: training-data
max_price_per_hour: 20.0
max_run_time_hours: 72.0
ssh_keys:
  - my-ssh-key
```

## Development Environment

The `flow dev` command provides a persistent development environment with fast, container-based execution. It's perfect for iterative development where you want to:
- Start a VM once and use it all day
- Run commands in isolated containers
- Reset environments quickly without restarting the VM
- Avoid the overhead of VM provisioning for each run

### Quick Start

```bash
# Start or connect to your dev VM (defaults to h100)
flow dev

# Run a command in a container
flow dev -c 'python train.py'

# Run interactive Python
flow dev -c python

# Use a specific Docker image
flow dev -c 'python test.py' --image pytorch/pytorch:latest

# Check dev environment status
flow dev --status

# Reset all containers (VM stays running)
flow dev --reset

# Stop the dev VM when done
flow dev --stop
```

### How It Works

1. **Persistent VM**: The first `flow dev` starts a VM that stays running
2. **Container Execution**: Each `flow dev -c` command runs in a fresh container
3. **Fast Iteration**: Containers start in seconds, not minutes
4. **Shared Workspace**: Your code is available at `/workspace` in all containers
5. **Automatic Cleanup**: Containers are removed after each command

### Uploading Code

Your dev VM needs access to your code. You have two options:

```bash
# Option 1: Auto-upload on VM creation (default)
flow dev  # Uploads current directory automatically

# Option 2: Manual upload later
flow dev --status  # Get your dev VM ID
flow upload-code <dev-vm-id>  # Upload code changes
```

### Examples

```bash
# Start dev environment with specific instance type
flow dev  # Defaults to h100
flow dev -i a100  # Use A100 instead
flow dev -i gpu.medium  # Or smaller instance

# Run training in a container
flow dev -c 'python train.py --epochs 10'

# Run Jupyter notebook
flow dev -c 'jupyter notebook --ip=0.0.0.0 --no-browser'

# Install dependencies and run
flow dev -c 'pip install -r requirements.txt && python app.py'

# Use GPU in container
flow dev -c 'nvidia-smi'

# Run with custom environment
flow dev -c 'python script.py' --image custom/ml-env:latest
```

### Comparison with `flow run`

| Feature | `flow dev` | `flow run` |
|---------|------------|------------|
| VM Lifecycle | Persistent (stays running) | Per-task (terminated after) |
| Startup Time | Fast (containers) | Slower (VM provisioning) |
| Use Case | Development/iteration | Production/long runs |
| Cost | Pay for VM uptime | Pay per task |
| Environment | Containers on VM | Direct on VM |

## Guide for SLURM Users

Flow SDK provides a modern cloud-native alternative to SLURM while maintaining compatibility with existing workflows. This guide helps SLURM users transition to Flow.

### Command Equivalents

| SLURM Command | Flow Command | Description |
|---------------|--------------|-------------|
| `sbatch job.sh` | `flow run job.yaml` | Submit batch job |
| `sbatch script.slurm` | `flow run script.slurm` | Direct SLURM script support |
| `squeue` | `flow status` | View job queue |
| `scancel <job_id>` | `flow cancel <task_id>` | Cancel job |
| `scancel -n <name_pattern>` | `flow cancel -n <pattern>` | Cancel by name pattern |
| `scontrol show job <id>` | `flow info <task_id>` | Show job details |
| `sacct` | *Not applicable* | Flow tracks costs differently |
| `sinfo` | *Not applicable* | Cloud resources are dynamic |
| `srun` | `flow dev -c` or `flow ssh` | Interactive access |

### Log Access

```bash
# SLURM: View output files
cat slurm-12345.out

# Flow: Stream logs directly
flow logs task-abc123
flow logs task-abc123 --follow    # Like tail -f
flow logs task-abc123 --stderr     # Error output
```

### SLURM Script Compatibility

Flow can directly run existing SLURM scripts:

```bash
# Your existing SLURM script
flow run job.slurm

# Behind the scenes, Flow parses #SBATCH directives:
#SBATCH --job-name=training
#SBATCH --nodes=2
#SBATCH --gpus=a100:4
#SBATCH --time=24:00:00
#SBATCH --mem=64G
```

### Migration Examples

#### Interactive Development (srun replacement)

**SLURM:**
```bash
# Interactive GPU session
srun --pty --gpus=1 --time=4:00:00 bash
srun --gpus=1 python train.py
```

**Flow (using flow dev):**
```bash
# Start persistent dev environment
flow dev  # Defaults to h100
flow dev -i a100  # Or specify A100

# Run commands in containers (like srun)
flow dev -c 'python train.py'
flow dev -c bash  # Interactive shell
```

#### Basic GPU Job

**SLURM:**
```bash
#!/bin/bash
#SBATCH --job-name=train-model
#SBATCH --partition=gpu
#SBATCH --gpus=1
#SBATCH --time=12:00:00
#SBATCH --mem=32G

module load cuda/11.8
python train.py
```

**Flow (YAML):**
```yaml
name: train-model
instance_type: a100
command: python train.py
max_run_time_hours: 12.0
```

**Flow (Python):**
```python
flow.run("python train.py", instance_type="a100", max_run_time_hours=12)
```

#### Multi-GPU Training

**SLURM:**
```bash
#!/bin/bash
#SBATCH --job-name=distributed
#SBATCH --nodes=4
#SBATCH --gpus-per-node=8
#SBATCH --ntasks-per-node=8

srun python -m torch.distributed.launch train.py
```

**Flow:**
```yaml
name: distributed
instance_type: 8xa100
num_instances: 4
command: |
  torchrun --nproc_per_node=8 --nnodes=4 \
    --node_rank=$FLOW_NODE_RANK \
    --master_addr=$FLOW_MAIN_IP \
    train.py
```

#### Array Jobs

**SLURM:**
```bash
#!/bin/bash
#SBATCH --array=1-10
#SBATCH --job-name=sweep

python experiment.py --task-id $SLURM_ARRAY_TASK_ID
```

**Flow (using loop):**
```python
for i in range(1, 11):
    flow.run(f"python experiment.py --task-id {i}", 
             name=f"sweep-{i}", instance_type="a100")
```

### Key Differences

1. **Resource Allocation**: Flow uses instance types (e.g., `a100`, `4xa100`) instead of partition/node specifications
2. **Cost Control**: Built-in `max_price_per_hour` instead of account-based billing
3. **Storage**: Cloud volumes (block storage) instead of shared filesystems
   - FCP platform supports both block storage and file shares
   - Flow SDK currently only creates block storage volumes (requires mounting/formatting)
   - File share support is planned for easier multi-node access
4. **Environment**: Container-based instead of module system
5. **Scheduling**: Cloud-native provisioning instead of queue-based scheduling

### Environment Variables

When using the SLURM adapter (`flow run script.slurm`), Flow sets SLURM-compatible environment variables:

| SLURM Variable | Set By SLURM Adapter | Flow Native Variable |
|----------------|---------------------|---------------------|
| `SLURM_JOB_ID` | ✓ (maps to `$FLOW_TASK_ID`) | `FLOW_TASK_ID` |
| `SLURM_JOB_NAME` | ✓ | `FLOW_TASK_NAME` |
| `SLURM_ARRAY_TASK_ID` | ✓ (planned) | - |
| `SLURM_NTASKS` | ✓ | - |
| `SLURM_CPUS_PER_TASK` | ✓ | - |
| `SLURM_NNODES` | ✓ | `FLOW_NODE_COUNT` |
| `SLURM_JOB_PARTITION` | ✓ (if set) | - |

For all Flow tasks (regardless of adapter), these variables are available:
- `FLOW_TASK_ID` - Unique task identifier
- `FLOW_TASK_NAME` - Task name from config

### Advanced Features

**Module System → Container Images:**
```yaml
# SLURM: module load pytorch/2.0
# Flow equivalent:
image: pytorch/pytorch:2.0.0-cuda11.8-cudnn8
```

**Dependency Management:**
```bash
# SLURM: --dependency=afterok:12345
# Flow: Use task.wait() in Python or chain commands
```

**Output Formatting:**
```bash
# Get SLURM-style output (coming soon)
flow status --format=slurm
```

### Future Compatibility

We're considering adding direct SLURM command aliases for easier migration:
- `flow sbatch` → `flow run`
- `flow squeue` → `flow status`
- `flow scancel` → `flow cancel`

If you need specific SLURM features, please [open an issue](https://github.com/foundrytechnologies/flow-v2/issues).

## Instance Types

| Type | GPUs | Total Memory |
|------|------|--------------|
| `a100` | 1x A100 | 80GB |
| `4xa100` | 4x A100 | 320GB |
| `8xa100` | 8x A100 | 640GB |
| `h100` | 8x H100 | 640GB |

```python
# Examples
flow.run("python train.py", instance_type="a100")     # Single GPU
flow.run("python train.py", instance_type="4xa100")   # Multi-GPU
flow.run("python train.py", instance_type="8xh100")   # Maximum performance
```

## Task Management

### Task Object

```python
# Get task handle
task = flow.run(config)
# Or retrieve existing
task = flow.get_task("task-abc123")

# Properties
task.task_id          # Unique identifier
task.status           # Current state
task.shell_command    # Shell connection string
task.cost_per_hour    # Current pricing
task.created_at       # Submission time

# Methods
task.wait(timeout=3600)       # Block until complete
task.refresh()                # Update status
task.cancel()                 # Terminate execution
```

### Logging

```python
# Get recent logs
logs = task.logs(tail=100)

# Stream in real-time
for line in task.logs(follow=True):
    if "loss:" in line:
        print(line)
```

### SSH Access

```python
# Interactive shell
task.shell()

# Run command
task.shell("nvidia-smi")
task.shell("tail -f /workspace/train.log")

# Multi-node access
task.shell(node=1)  # Connect to specific node
```

### Extended Information

```python
# Get task creator
user = task.get_user()
print(f"Created by: {user.username} ({user.email})")

# Get instance details
instances = task.get_instances()
for inst in instances:
    print(f"Node {inst.instance_id}:")
    print(f"  Public IP: {inst.public_ip}")
    print(f"  Private IP: {inst.private_ip}")
    print(f"  Status: {inst.status}")
```

## Persistent Storage

### Volume Management

```python
# Create volume (currently creates block storage)
with Flow() as client:
    vol = client.create_volume(size_gb=1000, name="datasets")

# Use in task
config = TaskConfig(
    name="training",
    instance_type="a100",
    command="python train.py",
    volumes=[{
        "volume_id": vol.volume_id,
        "mount_path": "/data"
    }]
)

# Or reference by name
config.volumes = [{
    "name": "datasets",
    "mount_path": "/data"
}]
```

### Dynamic Volume Mounting

Mount volumes to already running tasks without restart:

```bash
# CLI usage
flow mount <volume> <task>

# Examples
flow mount vol_abc123 task_xyz789      # By IDs
flow mount training-data gpu-job-1      # By names
flow mount :1 :2                        # By indices
```

```python
# Python API
flow.mount_volume("training-data", task.task_id)
# Volume available at /mnt/training-data immediately
```

**Multi-Instance Tasks**: 
- **Block volumes**: Cannot be mounted to multi-instance tasks (block storage limitation)
- **File shares**: Can be mounted to all instances simultaneously (when `interface="file"`)

**Note**: Flow SDK currently creates block storage volumes, which need to be formatted on first use. The underlying FCP platform also supports file shares (pre-formatted, multi-node accessible), but this is not yet exposed in the SDK.

### Docker Cache Optimization

Speed up container starts by caching Docker images:

```python
# Create a persistent cache volume
cache = flow.create_volume(size_gb=100, name="docker-cache")

# Use it in your tasks
task = flow.run(
    "python train.py",
    instance_type="a100",
    image="pytorch/pytorch:2.0.0-cuda11.8-cudnn8",
    volumes=[{
        "volume_id": cache.volume_id,
        "mount_path": "/var/lib/docker"
    }]
)
# First run: ~5 minutes (downloads image)
# Subsequent runs: ~30 seconds (uses cache)
```

## Zero-Import Remote Execution

Flow SDK's `invoke()` function lets you run Python functions on GPUs without modifying your code:

### The Invoker Pattern

```python
# train.py - Your existing code, no Flow imports needed
def train_model(data_path: str, epochs: int = 100):
    import torch
    model = torch.nn.Linear(10, 1)
    # ... training logic ...
    return {"accuracy": 0.95, "loss": 0.01}
```

```python
# runner.py - Execute remotely on GPU
from flow import invoke

result = invoke(
    "train.py",              # Python file
    "train_model",           # Function name  
    args=["s3://data"],      # Arguments
    kwargs={"epochs": 200},  # Keyword arguments
    gpu="a100"               # GPU type
)
print(result)  # {"accuracy": 0.95, "loss": 0.01}
```

### Why Use invoke()?

- **Zero contamination**: Keep ML code pure Python
- **Easy testing**: Run functions locally without changes
- **Flexible**: Any function, any module
- **Type safe**: JSON serialization ensures compatibility

See the [Invoker Pattern Guide](docs/INVOKER_PATTERN.md) for detailed documentation.

## Decorator Pattern

Flow SDK provides a decorator-based API similar to popular serverless frameworks:

### Basic Usage

```python
from flow import FlowApp

app = FlowApp()

@app.function(gpu="a100")
def train_model(data_path: str, epochs: int = 100):
    import torch
    model = torch.nn.Linear(10, 1)
    # ... training logic ...
    return {"accuracy": 0.95, "loss": 0.01}

# Execute remotely on GPU
result = train_model.remote("s3://data.csv", epochs=50)

# Execute locally for testing
local_result = train_model("./local_data.csv")
```

### Advanced Configuration

```python
@app.function(
    gpu="h100:8",  # 8x H100 GPUs
    image="pytorch/pytorch:2.0.0",
    volumes={"/data": "training-data"},
    env={"WANDB_API_KEY": "..."}
)
def distributed_training(config_path: str):
    # Multi-GPU training code
    return {"status": "completed"}

# Async execution
task_id = distributed_training.spawn("config.yaml")
```

### Module-Level Usage

```python
from flow import function

# Use without creating an app instance
@function(gpu="a100")
def inference(text: str) -> dict:
    # Run inference
    return {"sentiment": "positive"}
```

The decorator pattern provides:
- **Clean syntax**: Familiar to Flask/FastAPI users
- **Local testing**: Call functions directly without infrastructure
- **Type safety**: Full IDE support and type hints
- **Flexibility**: Mix local and remote execution seamlessly

## Data Mounting

Flow SDK provides seamless data access from S3 and volumes through the Flow client API:

### Quick Start

```python
# Mount S3 dataset
from flow import Flow

with Flow() as client:
    task = client.submit(
        "python train.py --data /data",
        gpu="a100",
        mounts="s3://my-bucket/datasets/imagenet"
    )

# Mount multiple sources
with Flow() as client:
    task = client.submit(
        "python train.py",
        gpu="a100:4",
        mounts={
            "/datasets": "s3://ml-bucket/imagenet",
            "/models": "volume://pretrained-models",  # Auto-creates if missing
            "/outputs": "volume://training-outputs"
        }
    )
```

### Supported Sources

- **S3**: Read-only access via s3fs (`s3://bucket/path`)
  - Requires AWS credentials in environment
  - Cached locally for performance
  
- **Volumes**: Persistent read-write storage (`volume://name`)
  - Auto-creates with 100GB if not found
  - High-performance NVMe storage

### Example: Training Pipeline

```python
# Set AWS credentials (from secure source)
import os
os.environ["AWS_ACCESS_KEY_ID"] = get_secret("aws_key")
os.environ["AWS_SECRET_ACCESS_KEY"] = get_secret("aws_secret")

# Submit training with data mounting
with Flow() as client:
    task = client.submit(
        """
        python train.py \\
            --data /datasets/train \\
            --validation /datasets/val \\
            --output /outputs
        """,
        gpu="a100:8",
        mounts={
            "/datasets": "s3://ml-datasets/imagenet",
            "/outputs": "volume://experiment-results"
        }
    )
```

See the [Data Mounting Guide](docs/DATA_MOUNTING_GUIDE.md) for detailed documentation.

## Distributed Training

### Single-Node Multi-GPU (Recommended)

```python
config = TaskConfig(
    name="distributed-training",
    instance_type="8xa100",  # 8x A100 GPUs on single node
    command="torchrun --nproc_per_node=8 --standalone train.py"
)
```

### Multi-Node Training

For multi-node training, explicitly set coordination environment variables:

```python
config = TaskConfig(
    name="multi-node-training",
    instance_type="8xa100",
    num_instances=4,  # 32 GPUs total
    env={
        "FLOW_NODE_RANK": "0",  # Set per node: 0, 1, 2, 3
        "FLOW_NUM_NODES": "4",
        "FLOW_MAIN_IP": "10.0.0.1"  # IP of rank 0 node
    },
    command=[
        "torchrun",
        "--nproc_per_node=8",
        "--nnodes=4",
        "--node_rank=$FLOW_NODE_RANK",
        "--master_addr=$FLOW_MAIN_IP",
        "--master_port=29500",
        "train.py"
    ]
)
```

## Advanced Features

### Cost Optimization

```python
# Use spot instances with price cap
config = TaskConfig(
    name="experiment",
    instance_type="a100",
    max_price_per_hour=5.0,  # Use spot if available
    max_run_time_hours=12.0  # Prevent runaway costs
)
```

### Environment Setup

```python
# Custom container
config.image = "pytorch/pytorch:2.0.0-cuda11.8-cudnn8"

# Environment variables
config.env = {
    "WANDB_API_KEY": "...",
    "HF_TOKEN": "...",
    "CUDA_VISIBLE_DEVICES": "0,1,2,3"
}

# Working directory
config.working_dir = "/workspace"
```

### Data Access

```python
# S3 integration
config = TaskConfig(
    name="s3-processing",
    instance_type="a100",
    command="python process.py",
    env={
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "..."
    }
)

# Or use mounts parameter (simplified API)
with Flow() as client:
    task = client.submit(
        "python analyze.py",
        gpu="a100",
        mounts={
            "/input": "s3://my-bucket/data/",
            "/output": "volume://results"
        }
    )
```

## Error Handling

Flow provides structured errors with recovery guidance:

```python
from flow.errors import (
    FlowError,
    AuthenticationError,
    ResourceNotFoundError,
    ValidationError,
    QuotaExceededError
)

try:
    task = flow.run(config)
except ValidationError as e:
    print(f"Configuration error: {e.message}")
    for suggestion in e.suggestions:
        print(f"  - {suggestion}")
except QuotaExceededError as e:
    print(f"Quota exceeded: {e.message}")
    print("Suggestions:", e.suggestions)
except FlowError as e:
    print(f"Error: {e}")
```

## Common Patterns

### Interactive Development

#### Development Environment (flow dev)

The `flow dev` command provides the fastest way to iterate on GPU code:

```bash
# Start a persistent dev VM (defaults to h100)
flow dev  # Creates h100 instance
flow dev -i a100  # Or specify different type

# Iterate quickly with containers
flow dev -c 'python experiment.py --lr 0.01'
flow dev -c 'python experiment.py --lr 0.001'
flow dev -c 'python experiment.py --lr 0.0001'

# Each command runs in seconds, not minutes!
```

#### Google Colab Integration

Connect Google Colab notebooks to Flow GPU instances:

```bash
# Launch GPU instance configured for Colab
flow colab connect --instance-type a100 --hours 4

# You'll receive:
# 1. SSH tunnel command to run locally
# 2. Connection URL for Colab
```

Then in Google Colab:
1. Go to Runtime → Connect to local runtime
2. Paste the connection URL
3. Click Connect

Your Colab notebook now runs on Flow GPU infrastructure!

#### Direct Jupyter Notebooks

Run Jupyter directly on Flow instances:

```python
# Launch Jupyter server
config = TaskConfig(
    name="notebook",
    instance_type="a100",
    command="jupyter lab --ip=0.0.0.0 --no-browser",
    ports=[8888],
    max_run_time_hours=8.0
)
task = flow.run(config)
print(f"Access at: {task.endpoints['jupyter']}")
```

### Checkpointing

```python
# Resume training from checkpoint
config = TaskConfig(
    name="resume-training",
    instance_type="a100",
    command="python train.py --resume",
    volumes=[{
        "name": "checkpoints",
        "mount_path": "/checkpoints"
    }]
)
```

### Experiment Sweep

```python
# Run multiple experiments
for lr in [0.001, 0.01, 0.1]:
    config = TaskConfig(
        name=f"exp-lr-{lr}",
        instance_type="a100",
        command=f"python train.py --lr {lr}",
        env={"WANDB_RUN_NAME": f"lr_{lr}"}
    )
    flow.run(config)
```

## Architecture

Flow SDK follows Domain-Driven Design with clear boundaries:

### High-Level Overview

```
┌─────────────────────────────────────────────┐
│          User Interface Layer               │
│        (Python API, CLI, YAML)              │
├─────────────────────────────────────────────┤
│           Core Domain Layer                 │
│     (TaskConfig, Task, Volume models)       │
├─────────────────────────────────────────────┤
│        Provider Abstraction Layer           │
│         (IProvider Protocol)                │
├─────────────────────────────────────────────┤
│        Provider Implementations             │
│     (FCP, AWS, GCP, Azure - future)         │
└─────────────────────────────────────────────┘
```

### Key Components

- **Flow SDK** (`src/flow/`): High-level Python SDK for ML/AI workloads
- **Mithril CLI** (`mithril/`): Low-level IaaS control following Unix philosophy
- **Provider Abstraction**: Cloud-agnostic interface for multi-cloud support

### Current Provider Support

**FCP (ML Foundry)** - Production Ready
- Ubuntu 22.04 environment with bash
- 10KB startup script limit
- Spot instances with preemption handling
- Block storage volumes (file shares available in some regions)
- See [FCP provider documentation](src/flow/providers/fcp/README.md) for implementation details

**AWS, GCP, Azure** - Planned
- Provider abstraction designed for multi-cloud
- Contributions welcome

### Additional Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and concepts
- [FCP Provider Details](src/flow/providers/fcp/README.md) - Provider-specific implementation
- [Colab Troubleshooting](docs/COLAB_TROUBLESHOOTING.md) - Colab setup guide
- [Configuration Guide](docs/CONFIGURATION.md) - Configuration options
- [Data Handling](docs/DATA_HANDLING.md) - Data management patterns

### Example Code

- [Verify Instance Setup](examples/01_verify_instance.py) - Basic GPU verification
- [Jupyter Server](examples/02_jupyter_server.py) - Launch Jupyter on GPU
- [Multi-Node Training](examples/03_multi_node_training.py) - Distributed training setup
- [S3 Data Access](examples/04_s3_data_access.py) - Cloud storage integration
- [More Examples](examples/) - Additional usage patterns

## Performance

- **Cold start**: 10-15 minutes (instance provisioning on FCP core)
- **Warm start**: 30-60 seconds (pre-allocated pool; pending feature: let FCP know if interesting)


## Troubleshooting

### Common Errors

**Authentication Failed**
```
Error: Invalid API key
```
Solution: Run `flow init` and ensure your API key is correct. Get a new key at [app.mlfoundry.com](https://app.mlfoundry.com/account/apikeys).

**No Available Instances**
```
Error: No instances available for type 'a100'
```
Solution: Try a different region or instance type. Check availability with `flow status`.

**Quota Exceeded**
```
Error: GPU quota exceeded in region us-east-1
```
Solution: Try a different region or contact support for quota increase.

**Invalid Instance Type**
```
ValidationError: Invalid instance type 'a100x8'
```
Solution: Use correct format: `8xa100` (not `a100x8`). See [Instance Types](#instance-types).

**Task Timeout**
```
Error: Task exceeded max_run_time_hours limit
```
Solution: Increase `max_run_time_hours` in your config or optimize your code.

**File Not Found**
```
python: can't open file 'train.py': No such file or directory
```
Solution: Ensure `upload_code=True` (default) or that your file exists in the Docker image.

**Module Not Found**
```
ModuleNotFoundError: No module named 'torch'
```
Solution: Install dependencies first: `flow.run("pip install torch && python train.py")`. See [Handling Dependencies](#handling-dependencies).

**Upload Size Limit**
```
Error: Project size (15.2MB) exceeds limit (10MB)
```
Note: Files are automatically compressed (gzip), but the 10MB limit applies after compression.

Solutions (in order of preference):
1. **Use .flowignore** to exclude unnecessary files (models, datasets, caches)
2. **Clone from Git**:
   ```python
   flow.run("git clone https://github.com/myorg/myrepo.git . && python train.py", 
            instance_type="a100", upload_code=False)
   ```
3. **Pre-built Docker image** with your code:
   ```python
   flow.run("python /app/train.py", instance_type="a100",
            image="myorg/myapp:latest", upload_code=False)
   ```
4. **Download from S3/GCS**:
   ```python
   flow.run("aws s3 cp s3://mybucket/code.tar.gz . && tar -xzf code.tar.gz && python train.py",
            instance_type="a100", upload_code=False)
   ```
5. **Mount code via volume** (for development):
   ```python
   # First upload to a volume manually, then:
   flow.run("python /code/train.py", instance_type="a100",
            volumes=[{"name": "my-code", "mount_path": "/code"}],
            upload_code=False)
   ```
   Note: Volumes are empty by default. You must manually populate them first (e.g., via git clone or rsync).

## Support

- **Issues**: [GitHub Issues](https://github.com/foundrytechnologies/flow-v2/issues)
- **Email**: support@mlfoundry.com

## License

Apache License 2.0 - see [LICENSE.txt](LICENSE.txt)