#!/usr/bin/env python3
"""
Test runner for Trickster Pi project.
Provides convenient test execution with different configurations.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", coverage=False, verbose=False, hardware=False):
    """Run tests with specified configuration."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html"])
    
    # Test selection based on type
    if test_type == "unit":
        cmd.extend(["-m", "not integration and not hardware"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "hardware":
        cmd.extend(["-m", "hardware"])
        if not hardware:
            print("Warning: Hardware tests require --hardware flag")
            return False
    elif test_type == "all":
        if hardware:
            # Run all tests including hardware
            pass
        else:
            # Run all tests except hardware
            cmd.extend(["-m", "not hardware"])
    
    # Add test directory
    cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with return code: {e.returncode}")
        return False


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="Trickster Pi Test Runner")
    
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "hardware", "all"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Verbose output"
    )
    
    parser.add_argument(
        "--hardware",
        action="store_true",
        help="Enable hardware tests (requires Raspberry Pi)"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", ".[dev]"
            ], check=True)
        except subprocess.CalledProcessError:
            print("Failed to install dependencies")
            return 1
    
    # Check if pytest is available
    try:
        subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("pytest not found. Install with: pip install pytest")
        return 1
    
    # Run tests
    success = run_tests(
        test_type=args.type,
        coverage=args.coverage,
        verbose=args.verbose,
        hardware=args.hardware
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
