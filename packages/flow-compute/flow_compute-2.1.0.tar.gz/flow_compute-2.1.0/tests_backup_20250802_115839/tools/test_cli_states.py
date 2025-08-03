#!/usr/bin/env python3
"""Test script to demonstrate CLI behavior with various API states.

This script uses the mock API server to test how the Flow CLI handles
different task states, including rare ones like 'preempting'.
"""

import os
import subprocess
import sys
import time
import requests
import json
from pathlib import Path


def setup_environment():
    """Set up environment to use mock API server."""
    # Use absolute path to ensure it overrides any existing config
    config_path = Path(__file__).parent.parent.absolute() / "config" / "mock_flow_config.yaml"
    os.environ["FLOW_CONFIG_FILE"] = str(config_path)
    
    # Also set individual environment variables as backup
    os.environ["FLOW_API_URL"] = "http://localhost:5555/api/v1"
    os.environ["FLOW_API_KEY"] = "test-mock-api-key"
    os.environ["FLOW_PROJECT"] = "test-project"
    
    print(f"✓ Set FLOW_CONFIG_FILE to: {config_path}")
    print(f"✓ Set FLOW_API_URL to: http://localhost:5555/api/v1")
    print(f"✓ Set FLOW_API_KEY to: test-mock-api-key")


def wait_for_server(url="http://localhost:5555/api/v1/health", timeout=30):
    """Wait for the mock server to be ready."""
    print("Waiting for mock server to start...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("\n✓ Mock server is ready")
                return True
        except (requests.ConnectionError, requests.Timeout) as e:
            print(".", end="", flush=True)
        time.sleep(0.5)
    raise TimeoutError("Mock server did not start in time")


def verify_mock_api_usage():
    """Verify that commands are using the mock API."""
    print("\nVerifying mock API connection...")
    
    # Make a test request to the mock API
    try:
        response = requests.get(
            "http://localhost:5555/api/v1/tasks?limit=1",
            headers={"Authorization": "Bearer test-mock-api-key"}
        )
        if response.status_code == 200:
            print("✓ Direct API request successful")
        else:
            print(f"✗ Direct API request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cannot connect to mock API: {e}")
        return False
    
    # Run a flow command and check if it hits the mock API
    print("\nTesting flow command routing...")
    
    # Create environment with our mock settings
    env = os.environ.copy()
    env["FLOW_CONFIG_FILE"] = str(Path(__file__).parent.parent.absolute() / "config" / "mock_flow_config.yaml")
    env["FLOW_API_URL"] = "http://localhost:5555/api/v1"
    env["FLOW_API_KEY"] = "test-mock-api-key"
    env["FLOW_PROJECT"] = "test-project"
    
    # First, let's see what flow is actually configured to use
    config_result = subprocess.run(
        "flow config show 2>/dev/null || echo 'No config command'",
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )
    
    result = subprocess.run(
        "flow status --limit 1 --json",
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            # Debug output
            print(f"  JSON response keys: {list(data.keys())}")
            
            # Check various indicators that we're using mock API
            if "tasks" in data:
                if len(data["tasks"]) == 0:
                    # No tasks yet, but successful response from mock
                    print("✓ Flow commands are using mock API (empty task list)")
                    return True
                else:
                    task = data["tasks"][0]
                    print(f"  First task: {task.get('name', 'unnamed')} by {task.get('created_by', 'unknown')}")
                    
                    # Check for mock API indicators
                    if (task.get("created_by") == "user_test123" or 
                        task.get("name", "").startswith("test-") or
                        "test" in str(task.get("task_id", ""))):
                        print("✓ Flow commands are using mock API")
                        return True
                    
            # If we get here, we're likely using real API
            print("✗ Flow commands appear to be using real API")
            print(f"  Full response: {json.dumps(data, indent=2)[:500]}...")
            return False
        except Exception as e:
            print(f"✗ Could not parse flow command output: {e}")
            print(f"  Raw output: {result.stdout[:200]}...")
            return False
    else:
        print(f"✗ Flow command failed with code {result.returncode}")
        print(f"  STDERR: {result.stderr[:200]}...")
        return False
    
    return True


def create_demo_tasks():
    """Create all demo task scenarios."""
    print("\nCreating demo tasks...")
    response = requests.post(
        "http://localhost:5555/api/v1/demo/create_all_scenarios",
        headers={"Authorization": "Bearer test-mock-api-key"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Created {len(data['tasks'])} demo tasks")
        return data['tasks']
    else:
        print(f"✗ Failed to create demo tasks: {response.status_code}")
        return []


def run_flow_command(command):
    """Run a flow command and capture output."""
    cmd_str = f"flow {command}"
    print(f"\n$ {cmd_str}")
    print("-" * 60)
    
    # Create environment with our mock settings
    env = os.environ.copy()
    env["FLOW_CONFIG_FILE"] = str(Path(__file__).parent.parent.absolute() / "config" / "mock_flow_config.yaml")
    env["FLOW_API_URL"] = "http://localhost:5555/api/v1"
    env["FLOW_API_KEY"] = "test-mock-api-key"
    env["FLOW_PROJECT"] = "test-project"
    
    result = subprocess.run(
        cmd_str,
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}", file=sys.stderr)
    
    return result


def demonstrate_status_command():
    """Demonstrate various status command outputs."""
    print("\n" + "=" * 80)
    print("DEMONSTRATING STATUS COMMAND WITH VARIOUS STATES")
    print("=" * 80)
    
    # Basic status
    print("\n1. Basic status showing all tasks:")
    run_flow_command("status")
    
    # Filter by status
    print("\n2. Filter by 'running' status:")
    run_flow_command("status --status running")
    
    print("\n3. Filter by 'preempting' status (rare state):")
    run_flow_command("status --status preempting")
    
    print("\n4. Filter by 'pending' status:")
    run_flow_command("status --status pending")
    
    print("\n5. Show all tasks with --all flag:")
    run_flow_command("status --all")
    
    # JSON output
    print("\n6. JSON output for automation:")
    result = run_flow_command("status --json")
    if result.stdout:
        try:
            data = json.loads(result.stdout)
            print(f"Found {len(data.get('tasks', []))} tasks in JSON format")
        except json.JSONDecodeError:
            pass


def demonstrate_task_transitions():
    """Demonstrate task state transitions."""
    print("\n" + "=" * 80)
    print("DEMONSTRATING TASK STATE TRANSITIONS")
    print("=" * 80)
    
    # Create a new task
    response = requests.post(
        "http://localhost:5555/api/v1/tasks",
        json={
            "name": "transition-demo",
            "status": "pending",
            "instance_type": "H100·80G"
        },
        headers={"Authorization": "Bearer test-mock-api-key"}
    )
    
    if response.status_code == 201:
        task = response.json()
        task_id = task['task_id']
        print(f"\n✓ Created task: {task_id}")
        
        # Show initial state
        print("\nInitial state (pending):")
        run_flow_command(f"status {task['name']}")
        
        # Transition to running
        print("\nTransitioning to 'running'...")
        requests.post(
            f"http://localhost:5555/api/v1/demo/transition_task/{task_id}",
            json={"status": "running"},
            headers={"Authorization": "Bearer test-mock-api-key"}
        )
        run_flow_command(f"status {task['name']}")
        
        # Transition to preempting
        print("\nTransitioning to 'preempting' (rare state)...")
        requests.post(
            f"http://localhost:5555/api/v1/demo/transition_task/{task_id}",
            json={"status": "preempting"},
            headers={"Authorization": "Bearer test-mock-api-key"}
        )
        run_flow_command(f"status {task['name']}")
        
        # Transition to cancelled
        print("\nTransitioning to 'cancelled'...")
        requests.post(
            f"http://localhost:5555/api/v1/demo/transition_task/{task_id}",
            json={"status": "cancelled"},
            headers={"Authorization": "Bearer test-mock-api-key"}
        )
        run_flow_command(f"status {task['name']}")


def demonstrate_edge_cases():
    """Demonstrate edge cases and error states."""
    print("\n" + "=" * 80)
    print("DEMONSTRATING EDGE CASES AND RARE STATES")
    print("=" * 80)
    
    # Preemption scenarios
    print("\n--- PREEMPTION SCENARIOS ---")
    print("\n1. Task being preempted (30 seconds warning):")
    run_flow_command("status preempting-task")
    
    print("\n2. Task that was preempted:")
    run_flow_command("status preempted-task")
    
    # Provisioning states
    print("\n--- PROVISIONING STATES ---")
    print("\n3. Instance initializing:")
    run_flow_command("status pending-init")
    
    print("\n4. Instance starting up:")
    run_flow_command("status pending-starting")
    
    print("\n5. Preparing environment:")
    run_flow_command("status preparing-env")
    
    print("\n6. Mounting volumes:")
    run_flow_command("status preparing-volumes")
    
    # Multi-node scenarios
    print("\n--- MULTI-NODE SCENARIOS ---")
    print("\n7. Distributed training (4 nodes):")
    run_flow_command("status distributed-training")
    
    print("\n8. Partial nodes ready (6/8):")
    run_flow_command("status partial-nodes")
    
    # SSH edge cases
    print("\n--- SSH/CONNECTIVITY ISSUES ---")
    print("\n9. Running without SSH keys:")
    run_flow_command("status no-ssh-task")
    
    print("\n10. SSH pending (network setup):")
    run_flow_command("status ssh-pending")
    
    print("\n11. NAT gateway (non-standard port):")
    run_flow_command("status nat-ssh")
    
    # Failed states
    print("\n--- FAILURE SCENARIOS ---")
    print("\n12. Out of memory error:")
    run_flow_command("status failed-oom")
    
    print("\n13. Startup script failed:")
    run_flow_command("status failed-startup")
    
    print("\n14. SSH timeout:")
    run_flow_command("status failed-ssh")
    
    print("\n15. Spot instance reclaimed:")
    run_flow_command("status failed-spot")
    
    # Billing edge cases
    print("\n--- BILLING/COST SCENARIOS ---")
    print("\n16. Free tier task:")
    run_flow_command("status free-tier")
    
    print("\n17. Discounted task:")
    run_flow_command("status discounted-task")
    
    # Special states
    print("\n--- SPECIAL/RARE STATES ---")
    print("\n18. Paused for maintenance:")
    run_flow_command("status paused-task")
    
    print("\n19. Relocating to different zone:")
    run_flow_command("status relocating-task")
    
    print("\n20. Scheduled future task:")
    run_flow_command("status scheduled-task")
    
    print("\n21. Kubernetes pod pending:")
    run_flow_command("status k8s-pending")


def demonstrate_status_filters():
    """Demonstrate various status filters and groupings."""
    print("\n" + "=" * 80)
    print("DEMONSTRATING STATUS FILTERS")
    print("=" * 80)
    
    # Group by rare states
    print("\n1. Show all preempting tasks:")
    run_flow_command("status --status preempting")
    
    print("\n2. Show all pending tasks (includes provisioning):")
    run_flow_command("status --status pending")
    
    print("\n3. Show failed tasks with details:")
    run_flow_command("status --status failed --verbose")
    
    print("\n4. Show high-value tasks (8×H100):")
    # This would need custom filtering in real implementation
    print("(Custom filter: tasks with instance_type containing '8×')")
    
    print("\n5. Show tasks with SSH issues:")
    # This would show tasks without SSH or with pending SSH
    print("(Custom filter: tasks with SSH warnings)")


def demonstrate_cost_tracking():
    """Demonstrate cost tracking and billing scenarios."""
    print("\n" + "=" * 80)
    print("DEMONSTRATING COST TRACKING")
    print("=" * 80)
    
    print("\n1. Calculate total GPU hours and costs:")
    result = run_flow_command("status --all --json")
    
    if result.stdout:
        try:
            import json
            data = json.loads(result.stdout)
            tasks = data.get('tasks', [])
            
            total_cost = 0
            gpu_hours = 0
            
            for task in tasks:
                # Parse cost from string like "$4.50"
                cost_str = task.get('cost_per_hour', '$0.00')
                cost = float(cost_str.replace('$', '').replace(',', ''))
                
                # Estimate runtime based on status
                if task['status'] == 'running':
                    # Assume running for 1 hour for demo
                    gpu_hours += 1
                    total_cost += cost
            
            print(f"\nTotal active GPU-hours: {gpu_hours}")
            print(f"Estimated hourly burn rate: ${total_cost:.2f}")
        except:
            pass


def main():
    """Main test execution."""
    print("Flow CLI State Testing")
    print("=" * 80)
    
    # Setup
    setup_environment()
    
    # Check if server is running
    try:
        wait_for_server()
    except TimeoutError:
        print("\n⚠️  Mock server is not running!")
        print("Please start it in another terminal with:")
        print("  cd tests && python utils/mock_api_server.py")
        sys.exit(1)
    
    # Verify mock API is being used
    if not verify_mock_api_usage():
        print("\n⚠️  Flow commands are not using the mock API!")
        print("\nPossible fixes:")
        print("1. Check if you have ~/.flow/config.yaml overriding settings")
        print("2. Try moving it temporarily:")
        print("   mv ~/.flow/config.yaml ~/.flow/config.yaml.backup")
        print("3. Or run commands with explicit config:")
        print(f"   FLOW_CONFIG_FILE={Path(__file__).parent.parent.absolute()}/config/mock_flow_config.yaml flow status")
        sys.exit(1)
    
    # Create demo data
    tasks = create_demo_tasks()
    if not tasks:
        print("Failed to create demo tasks")
        sys.exit(1)
    
    # Run demonstrations
    demonstrate_status_command()
    demonstrate_task_transitions()
    demonstrate_edge_cases()
    demonstrate_status_filters()
    demonstrate_cost_tracking()
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("\nYou can explore further by:")
    print("  - Running individual flow commands")
    print("  - Creating custom task states via the API")
    print("  - Testing error scenarios")
    print("\n💡 TIP: Watch the mock server terminal to see API requests!")
    print("Each command should show requests like:")
    print('  INFO:werkzeug:127.0.0.1 - - [date] "GET /api/v1/tasks HTTP/1.1" 200')
    print("=" * 80)


if __name__ == "__main__":
    main()