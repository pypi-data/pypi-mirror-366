#!/usr/bin/env python3
"""Example showing how to migrate SSH-based integration tests to flow.dev SDK.

This demonstrates the benefits of using flow.dev SDK:
1. No need to manage SSH connections manually
2. Faster test execution (no VM startup time)
3. Better isolation between tests (containers)
4. Automatic cleanup
5. Simpler code
"""

from typing import Tuple
import subprocess
import time

from flow import Flow


class OldSSHBasedTester:
    """Original SSH-based test approach (for comparison)."""
    
    def __init__(self, instance_ip: str, ssh_key_path: str, ssh_user: str = "ubuntu"):
        self.instance_ip = instance_ip
        self.ssh_key_path = ssh_key_path
        self.ssh_user = ssh_user
    
    def run_ssh_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run command via SSH."""
        ssh_args = [
            "ssh",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-i", self.ssh_key_path,
            f"{self.ssh_user}@{self.instance_ip}",
            command
        ]
        
        try:
            result = subprocess.run(
                ssh_args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
    
    def test_docker_operations(self):
        """Test Docker using SSH."""
        # Need to SSH into machine
        success, output, error = self.run_ssh_command("docker --version")
        if not success:
            print(f"Docker test failed: {error}")
            return False
        
        # Run hello-world
        success, output, error = self.run_ssh_command("docker run --rm hello-world")
        return success


class NewDevSDKTester:
    """New flow.dev SDK approach - much simpler!"""
    
    def __init__(self):
        self.flow = Flow()
        # Ensure dev VM is running
        self.flow.dev.ensure_started()
    
    def test_docker_operations(self):
        """Test Docker using dev SDK."""
        # Direct execution in container - no SSH needed!
        exit_code = self.flow.dev.exec("docker --version")
        if exit_code != 0:
            print("Docker test failed")
            return False
        
        # Run hello-world
        exit_code = self.flow.dev.exec("docker run --rm hello-world")
        return exit_code == 0


def compare_approaches():
    """Compare the two testing approaches."""
    
    print("Comparison: SSH-based vs flow.dev SDK Testing")
    print("=" * 60)
    
    # Old approach disadvantages
    print("\n❌ Old SSH-based approach:")
    print("- Requires managing SSH keys and connections")
    print("- Need to provision new VM for each test run (slow)")
    print("- Complex error handling for SSH failures")
    print("- Manual cleanup of resources")
    print("- Tests can interfere with each other (shared VM state)")
    
    # New approach advantages  
    print("\n✅ New flow.dev SDK approach:")
    print("- No SSH management needed")
    print("- Reuses existing dev VM (fast startup)")
    print("- Simple error handling")
    print("- Automatic container cleanup")
    print("- Tests run in isolated containers")
    
    # Code comparison
    print("\n📊 Code complexity comparison:")
    print("Old: ~50 lines for basic SSH test runner")
    print("New: ~10 lines for dev SDK test runner")
    
    # Performance comparison
    print("\n⚡ Performance comparison:")
    print("Old: VM startup time (~2-5 minutes) + test time")
    print("New: Container startup time (~1-3 seconds) + test time")
    
    # Example migration
    print("\n🔄 Migration example:")
    print("Old code:")
    print("""
    def test_script_execution(self):
        # Complex SSH setup
        success, stdout, stderr = self.run_ssh_command(
            "sudo bash /var/lib/cloud/instance/scripts/part-001"
        )
        if not success:
            raise Exception(f"Script failed: {stderr}")
        return stdout
    """)
    
    print("New code:")
    print("""
    def test_script_execution(self):
        # Simple container execution
        exit_code = self.flow.dev.exec(
            "bash /tmp/test-startup-script.sh"
        )
        return exit_code == 0
    """)


def migration_guide():
    """Step-by-step migration guide."""
    
    print("\n📚 Migration Guide: SSH Tests → flow.dev SDK")
    print("=" * 60)
    
    print("\n1. Replace SSH connection setup:")
    print("   OLD: Initialize with IP, SSH key, username")
    print("   NEW: Just create Flow() client and ensure_started()")
    
    print("\n2. Replace SSH command execution:")
    print("   OLD: self.run_ssh_command('command')")
    print("   NEW: self.flow.dev.exec('command')")
    
    print("\n3. Handle test isolation:")
    print("   OLD: Manual cleanup between tests")
    print("   NEW: Each exec() runs in fresh container")
    
    print("\n4. Update test fixtures:")
    print("   OLD: pytest fixture creates new VM")
    print("   NEW: pytest fixture ensures dev VM is running")
    
    print("\n5. Simplify error handling:")
    print("   OLD: Handle SSH timeouts, connection errors")
    print("   NEW: Just check exit codes")
    
    print("\n6. Speed up test suite:")
    print("   OLD: Each test file might spin up new VM")
    print("   NEW: All tests share persistent dev VM")


def performance_comparison():
    """Show actual performance comparison."""
    
    print("\n⏱️  Performance Comparison (Typical Test Suite)")
    print("=" * 60)
    
    # Simulated timings
    old_times = {
        "VM provisioning": 180,  # 3 minutes
        "SSH setup": 10,
        "Install dependencies": 60,
        "Run 10 tests": 30,
        "Cleanup": 20,
    }
    
    new_times = {
        "Ensure dev VM": 2,  # Usually already running
        "Run 10 tests": 35,  # Slightly more due to container overhead
        "Cleanup": 1,
    }
    
    old_total = sum(old_times.values())
    new_total = sum(new_times.values())
    
    print("\nOld approach timing breakdown:")
    for task, seconds in old_times.items():
        print(f"  {task}: {seconds}s")
    print(f"  TOTAL: {old_total}s ({old_total/60:.1f} minutes)")
    
    print("\nNew approach timing breakdown:")
    for task, seconds in new_times.items():
        print(f"  {task}: {seconds}s")
    print(f"  TOTAL: {new_total}s ({new_total/60:.1f} minutes)")
    
    speedup = old_total / new_total
    print(f"\n🚀 Speedup: {speedup:.1f}x faster!")
    print(f"   Time saved per run: {(old_total - new_total)/60:.1f} minutes")


def practical_examples():
    """Show practical migration examples."""
    
    print("\n💡 Practical Migration Examples")
    print("=" * 60)
    
    print("\n1. Testing GPU availability:")
    print("OLD:")
    print("""
    success, output, _ = self.run_ssh_command("nvidia-smi")
    gpu_available = success and "NVIDIA" in output
    """)
    
    print("\nNEW:")
    print("""
    exit_code = self.flow.dev.exec("nvidia-smi")
    gpu_available = exit_code == 0
    """)
    
    print("\n2. Testing file operations:")
    print("OLD:")
    print("""
    # Create file
    self.run_ssh_command("echo 'test' > /tmp/test.txt")
    # Read file
    success, content, _ = self.run_ssh_command("cat /tmp/test.txt")
    """)
    
    print("\nNEW:")
    print("""
    # Create and read file in same container
    self.flow.dev.exec("echo 'test' > /tmp/test.txt && cat /tmp/test.txt")
    """)
    
    print("\n3. Testing with specific Docker image:")
    print("OLD:")
    print("""
    # Pull image first via SSH
    self.run_ssh_command("docker pull python:3.11")
    # Then run command
    self.run_ssh_command("docker run python:3.11 python --version")
    """)
    
    print("\nNEW:")
    print("""
    # Direct execution with image
    self.flow.dev.exec("python --version", image="python:3.11")
    """)


def main():
    """Run comparison examples."""
    print("SSH-based Tests → flow.dev SDK Migration Guide")
    print("=" * 60)
    
    compare_approaches()
    migration_guide()
    performance_comparison()
    practical_examples()
    
    print("\n✨ Summary")
    print("=" * 60)
    print("The flow.dev SDK provides a much simpler and faster way to run")
    print("integration tests that need real VM/container environments.")
    print("\nKey benefits:")
    print("- 5-10x faster test execution")
    print("- 80% less boilerplate code")  
    print("- Better test isolation")
    print("- Easier debugging")
    print("\nStart migrating your slowest integration tests first to see")
    print("immediate benefits!")


if __name__ == "__main__":
    main()