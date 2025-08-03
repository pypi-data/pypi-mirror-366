#!/usr/bin/env python3
"""Discover FCP instances and run integration tests.

This script can discover running FCP instances or use provided IPs.
"""

import argparse
import subprocess
import sys
from typing import List


def discover_fcp_instances() -> List[str]:
    """Discover running FCP instances using Flow CLI.
    
    Returns:
        List of instance IP addresses
    """
    try:
        # Try using flow task list to find running instances
        result = subprocess.run(
            ["flow", "task", "list", "--state", "running", "--json"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            import json
            tasks = json.loads(result.stdout)
            ips = []
            for task in tasks:
                if task.get("ssh_host"):
                    ips.append(task["ssh_host"])
            return ips
    except Exception as e:
        print(f"Could not discover instances via Flow CLI: {e}")

    return []


def run_test_suite(test_script: str, instance_ips: List[str], ssh_key: str) -> bool:
    """Run a test script against instances.
    
    Args:
        test_script: Path to test script
        instance_ips: List of instance IPs
        ssh_key: SSH key path
        
    Returns:
        True if tests passed
    """
    cmd = ["python", test_script] + instance_ips + ["--key", ssh_key]

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)

    return result.returncode == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Discover and test FCP instances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Discover instances automatically
    %(prog)s --discover --key ~/.ssh/flow_key
    
    # Use specific instances
    %(prog)s 18.144.35.49 54.177.129.4 --key ~/.ssh/flow_key
    
    # Run specific test suite
    %(prog)s --discover --key ~/.ssh/flow_key --test docker
        """
    )

    parser.add_argument(
        "instances",
        nargs="*",
        help="Instance IP addresses (if not using --discover)"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Automatically discover running FCP instances"
    )
    parser.add_argument(
        "--key",
        required=True,
        help="SSH private key path"
    )
    parser.add_argument(
        "--test",
        choices=["all", "docker", "startup", "logs", "critical", "access"],
        default="access",
        help="Which test suite to run (default: access)"
    )

    args = parser.parse_args()

    # Get instance IPs
    if args.discover:
        print("Discovering FCP instances...")
        instance_ips = discover_fcp_instances()
        if not instance_ips:
            print("No running instances found via Flow CLI")
            print("Falling back to manual specification")
    else:
        instance_ips = args.instances

    if not instance_ips:
        print("Error: No instances specified and discovery failed")
        print("Please provide instance IPs or ensure Flow CLI is configured")
        sys.exit(1)

    print(f"Testing instances: {', '.join(instance_ips)}")

    # Map test names to scripts
    test_scripts = {
        "access": "verify_instance_access.py",
        "docker": "test_docker_integration.py",
        "startup": "test_startup_scripts_integration.py",
        "logs": "test_logs_integration.py",
        "critical": "test_critical_features.py",
        "all": "test_fcp_live_instances.py"
    }

    script = test_scripts[args.test]

    # Run the test
    success = run_test_suite(script, instance_ips, args.key)

    if success:
        print("\n✅ Tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
