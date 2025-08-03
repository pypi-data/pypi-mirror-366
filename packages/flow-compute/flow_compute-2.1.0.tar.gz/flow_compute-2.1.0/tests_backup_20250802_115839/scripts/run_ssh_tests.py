"""Test runner for SSH functionality tests.

Provides different test execution strategies based on available time and resources.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


class SSHTestRunner:
    """Orchestrate SSH test execution with different strategies."""

    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.slow_tests = []
        self.fast_tests = []
        self.categorize_tests()

    def categorize_tests(self):
        """Categorize tests by execution time."""
        # Fast tests (seconds)
        self.fast_tests = [
            "tests/unit/test_ssh_logs.py",
            "tests/unit/test_ssh_key_manager_security.py",
            "tests/unit/test_ssh_multi_node.py",
            "tests/unit/test_ssh_tunnels.py",
            "tests/integration/test_ssh_integration.py",
        ]

        # Slow tests (10+ minutes)
        self.slow_tests = [
            "tests/e2e/test_ssh_e2e.py",
        ]

    def run_fast_tests(self):
        """Run only fast SSH tests."""
        print("Running fast SSH tests...")
        cmd = ["pytest", "-v", "-m", "not slow"] + self.fast_tests
        return subprocess.run(cmd, cwd=self.test_dir.parent).returncode

    def run_slow_tests(self):
        """Run slow E2E tests with proper configuration."""
        print("Running slow SSH E2E tests...")
        print("This will take 10-20 minutes for instance startup.")

        # Check configuration
        if not os.getenv("FCP_API_KEY"):
            print("ERROR: FCP_API_KEY not set. E2E tests require authentication.")
            return 1

        if not os.getenv("FLOW_E2E_TESTS_ENABLED"):
            print("ERROR: FLOW_E2E_TESTS_ENABLED not set. Set to 1 to enable E2E tests.")
            return 1

        cmd = ["pytest", "-v", "-m", "slow", "--run-slow"] + self.slow_tests
        return subprocess.run(cmd, cwd=self.test_dir.parent).returncode

    def run_all_tests(self):
        """Run all SSH tests."""
        print("Running all SSH tests...")

        # Run fast tests first
        fast_result = self.run_fast_tests()
        if fast_result != 0:
            print("\nFast tests failed. Skipping slow tests.")
            return fast_result

        print("\nFast tests passed. Running slow tests...")
        return self.run_slow_tests()

    def run_ci_tests(self):
        """Run tests suitable for CI/CD pipelines."""
        print("Running CI-friendly SSH tests...")

        # Only run fast tests in CI
        cmd = [
            "pytest", "-v",
            "-m", "not slow and not e2e",
            "--cov=flow",
            "--cov-report=xml",
            "--cov-report=term-missing"
        ] + self.fast_tests

        return subprocess.run(cmd, cwd=self.test_dir.parent).returncode

    def run_nightly_tests(self):
        """Run comprehensive tests for nightly builds."""
        print("Running nightly SSH test suite...")

        # Set up environment for nightly tests
        env = os.environ.copy()
        env["FLOW_E2E_TESTS_ENABLED"] = "1"

        cmd = [
            "pytest", "-v",
            "--run-slow",
            "-x",  # Stop on first failure
            "--tb=short"
        ] + self.fast_tests + self.slow_tests

        return subprocess.run(cmd, cwd=self.test_dir.parent, env=env).returncode

    def print_test_summary(self):
        """Print summary of available tests."""
        print("SSH Test Suite Summary")
        print("=" * 50)
        print(f"Fast tests ({len(self.fast_tests)}):")
        for test in self.fast_tests:
            print(f"  - {test}")
        print(f"\nSlow tests ({len(self.slow_tests)}):")
        for test in self.slow_tests:
            print(f"  - {test}")
        print("\nExecution strategies:")
        print("  --fast     : Run only fast tests (< 1 minute)")
        print("  --slow     : Run only slow tests (10-20 minutes)")
        print("  --all      : Run all tests")
        print("  --ci       : Run CI-friendly tests")
        print("  --nightly  : Run comprehensive nightly suite")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run SSH functionality tests")
    parser.add_argument(
        "--fast", action="store_true",
        help="Run only fast tests"
    )
    parser.add_argument(
        "--slow", action="store_true",
        help="Run only slow E2E tests"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all tests"
    )
    parser.add_argument(
        "--ci", action="store_true",
        help="Run CI-friendly tests"
    )
    parser.add_argument(
        "--nightly", action="store_true",
        help="Run nightly test suite"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Print test summary"
    )

    args = parser.parse_args()
    runner = SSHTestRunner()

    if args.summary or not any([args.fast, args.slow, args.all, args.ci, args.nightly]):
        runner.print_test_summary()
        return 0

    start_time = time.time()

    if args.fast:
        result = runner.run_fast_tests()
    elif args.slow:
        result = runner.run_slow_tests()
    elif args.all:
        result = runner.run_all_tests()
    elif args.ci:
        result = runner.run_ci_tests()
    elif args.nightly:
        result = runner.run_nightly_tests()
    else:
        result = runner.run_fast_tests()  # Default to fast tests

    elapsed = time.time() - start_time
    print(f"\nTest execution completed in {elapsed:.1f} seconds")

    return result


if __name__ == "__main__":
    sys.exit(main())
