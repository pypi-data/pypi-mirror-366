#!/usr/bin/env python3
"""Test runner script with marker-based test selection.

This script demonstrates how to run tests by category using pytest markers.
"""

import argparse
import subprocess
import sys
from typing import List, Optional


def run_tests(markers: Optional[List[str]] = None, extra_args: Optional[List[str]] = None) -> int:
    """Run tests with specified markers."""
    cmd = ["pytest"]
    
    if markers:
        marker_expr = " and ".join(markers)
        cmd.extend(["-m", marker_expr])
    
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser(description="Run Flow SDK tests by category")
    
    # Test categories
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", 
        action="store_true",
        help="Run integration tests only"
    )
    parser.add_argument(
        "--e2e",
        action="store_true", 
        help="Run end-to-end tests only"
    )
    
    # Test characteristics
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests only (< 1 second)"
    )
    parser.add_argument(
        "--no-slow",
        action="store_true",
        help="Exclude slow tests"
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Exclude tests requiring network"
    )
    
    # Specific test types
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Run GPU-related tests"
    )
    parser.add_argument(
        "--distributed",
        action="store_true",
        help="Run distributed/multi-node tests"
    )
    
    # Other options
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel",
        "-n",
        type=str,
        default="auto",
        help="Number of parallel workers (default: auto)"
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    # Build marker expression
    markers = []
    
    # Category markers
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.e2e:
        markers.append("e2e")
    
    # Characteristic markers
    if args.quick:
        markers.append("quick")
    if args.no_slow:
        markers.append("not slow")
    if args.no_network:
        markers.append("not network")
    
    # Specific type markers
    if args.gpu:
        markers.append("gpu")
    if args.distributed:
        markers.append("distributed")
    
    # Build extra arguments
    extra_args = []
    
    if args.coverage:
        extra_args.extend(["--cov=flow", "--cov-report=html", "--cov-report=term"])
    
    if args.verbose:
        extra_args.append("-vv")
    
    if args.parallel != "auto":
        extra_args.extend(["-n", args.parallel])
    
    # Add any additional pytest arguments
    extra_args.extend(args.pytest_args)
    
    # Run tests
    return run_tests(markers, extra_args)


if __name__ == "__main__":
    sys.exit(main())


# Example usage:
# ./run_tests.py --unit                    # Run all unit tests
# ./run_tests.py --unit --quick            # Run quick unit tests
# ./run_tests.py --integration --no-slow   # Run integration tests, exclude slow ones
# ./run_tests.py --unit --coverage         # Run unit tests with coverage
# ./run_tests.py --gpu                     # Run GPU-related tests
# ./run_tests.py --unit --no-network       # Run unit tests that don't need network