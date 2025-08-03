#!/usr/bin/env python3
"""Quick verification script for FCP instance access.

This script helps verify SSH access to running FCP instances and 
provides guidance on setting up proper authentication.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def check_ssh_command_available() -> bool:
    """Check if SSH command is available."""
    try:
        subprocess.run(["ssh", "-V"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


def find_ssh_keys() -> List[Tuple[str, str]]:
    """Find potential SSH keys for FCP access.
    
    Returns:
        List of (private_key_path, description) tuples
    """
    keys = []

    # Check environment variable
    if env_key := os.environ.get("FCP_SSH_KEY"):
        if Path(env_key).exists():
            keys.append((env_key, "From FCP_SSH_KEY environment variable"))

    # Check Flow keys directory
    flow_keys = Path.home() / ".flow" / "keys"
    if flow_keys.exists():
        for key_file in flow_keys.iterdir():
            if key_file.is_file() and not key_file.name.endswith('.pub'):
                keys.append((str(key_file), f"Flow auto-generated key: {key_file.name}"))

    # Check standard SSH directory
    ssh_dir = Path.home() / ".ssh"
    if ssh_dir.exists():
        # Look for common key names
        common_names = ["id_ed25519", "id_rsa", "id_ecdsa", "fcp", "flow"]
        for name in common_names:
            key_path = ssh_dir / name
            if key_path.exists() and key_path.is_file():
                keys.append((str(key_path), f"Standard SSH key: {name}"))

    return keys


def test_ssh_connection(host: str, user: str = "ubuntu", port: int = 22,
                       key_path: Optional[str] = None) -> Tuple[bool, str]:
    """Test SSH connection to a host.
    
    Returns:
        Tuple of (success, output_or_error)
    """
    ssh_args = [
        "ssh",
        "-o", "ConnectTimeout=10",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PasswordAuthentication=no",
        "-p", str(port),
    ]

    if key_path:
        ssh_args.extend(["-i", key_path])

    ssh_args.extend([
        f"{user}@{host}",
        "echo 'SSH_TEST_SUCCESS' && uname -a"
    ])

    try:
        result = subprocess.run(
            ssh_args,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0 and "SSH_TEST_SUCCESS" in result.stdout:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip() or f"Exit code: {result.returncode}"

    except subprocess.TimeoutExpired:
        return False, "Connection timeout"
    except Exception as e:
        return False, str(e)


def verify_instance_access(instances: List[str], ssh_user: str = "ubuntu") -> None:
    """Verify SSH access to FCP instances.
    
    Args:
        instances: List of instance IP addresses
        ssh_user: SSH username (default: ubuntu)
    """
    print("FCP Instance Access Verification")
    print("=" * 50)

    # Check SSH availability
    if not check_ssh_command_available():
        print("ERROR: SSH command not found. Please install OpenSSH.")
        sys.exit(1)

    # Find available SSH keys
    print("\n1. Searching for SSH keys...")
    ssh_keys = find_ssh_keys()

    if not ssh_keys:
        print("WARNING: No SSH keys found!")
        print("\nTo set up SSH access:")
        print("1. Set FCP_SSH_KEY environment variable to your private key path")
        print("2. Or ensure Flow has auto-generated keys in ~/.flow/keys/")
        print("3. Or use standard SSH keys in ~/.ssh/")

        # Try without explicit key (relies on ssh-agent or default keys)
        ssh_keys = [(None, "Default SSH configuration")]
    else:
        print(f"Found {len(ssh_keys)} potential SSH keys:")
        for key_path, desc in ssh_keys:
            print(f"  - {desc}")
            if key_path:
                print(f"    Path: {key_path}")

    # Test each instance with each key
    print(f"\n2. Testing SSH access to {len(instances)} instances...")

    results = {}
    for instance_ip in instances:
        print(f"\nTesting instance: {instance_ip}")
        instance_results = []

        for key_path, key_desc in ssh_keys:
            print(f"  Trying {key_desc}...", end=" ", flush=True)

            success, output = test_ssh_connection(
                host=instance_ip,
                user=ssh_user,
                key_path=key_path
            )

            if success:
                print("✓ SUCCESS")
                print(f"    System info: {output.split('\\n')[-1]}")
                instance_results.append((True, key_path, key_desc))
                break  # Found working key, no need to try others
            else:
                print("✗ FAILED")
                if "Permission denied" in output:
                    print("    Error: Permission denied (wrong key)")
                elif "Connection refused" in output:
                    print("    Error: Connection refused (SSH not ready or wrong port)")
                elif "timeout" in output.lower():
                    print("    Error: Connection timeout (network issue or instance not ready)")
                else:
                    print(f"    Error: {output[:100]}...")
                instance_results.append((False, key_path, output))

        results[instance_ip] = instance_results

    # Summary
    print("\n3. Summary")
    print("-" * 50)

    successful_instances = []
    failed_instances = []

    for instance_ip, attempts in results.items():
        success = any(attempt[0] for attempt in attempts)
        if success:
            successful_instances.append(instance_ip)
            working_key = next(a[1] for a in attempts if a[0])
            print(f"✓ {instance_ip}: Accessible")
            if working_key:
                print(f"    Working key: {working_key}")
        else:
            failed_instances.append(instance_ip)
            print(f"✗ {instance_ip}: Not accessible")

    print(f"\nAccessible instances: {len(successful_instances)}/{len(instances)}")

    if successful_instances:
        print("\n4. Next Steps")
        print("-" * 50)
        print("You can now run the full integration test suite:")
        print("  python tests/test_fcp_live_instances.py")
        print("\nOr connect manually to test:")
        for ip in successful_instances:
            print(f"  ssh ubuntu@{ip}")

    else:
        print("\n4. Troubleshooting")
        print("-" * 50)
        print("No instances were accessible. Common issues:")
        print("1. SSH keys not properly configured with FCP")
        print("2. Instances still starting up (can take 10-20 minutes)")
        print("3. Security group/firewall blocking SSH (port 22)")
        print("4. Wrong SSH user (default is 'ubuntu')")
        print("\nTo debug further:")
        print("- Check if instances show the correct SSH key in FCP console")
        print("- Verify instances are in 'running' state")
        print("- Try: ssh -vvv ubuntu@<instance-ip> for detailed debug output")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify SSH access to FCP instances"
    )
    parser.add_argument(
        "instances",
        nargs="+",
        help="Instance IP addresses to test"
    )
    parser.add_argument(
        "--user",
        default="ubuntu",
        help="SSH username (default: ubuntu)"
    )

    args = parser.parse_args()

    verify_instance_access(args.instances, args.user)


if __name__ == "__main__":
    main()
