#!/usr/bin/env python3
"""Test runner for CLI display storage fixes.

This script runs all tests related to the CLI fixes with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all CLI-related tests with coverage."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Test files to run
    test_files = [
        "test_cli_display_fixes.py",
        "test_cli_integration.py",
        "test_cli_regression.py"
    ]
    
    print("=" * 70)
    print("Running CLI Display Storage Fix Tests")
    print("=" * 70)
    print()
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--cov=vector_db_query.cli",
        "--cov=vector_db_query.vector_db",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov_cli",
        "-x",  # Stop on first failure
        "--tb=short"
    ] + test_files
    
    print(f"Executing: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=test_dir)
    
    print()
    print("=" * 70)
    
    if result.returncode == 0:
        print("✅ All tests passed!")
        print()
        print("Coverage report generated in: htmlcov_cli/index.html")
    else:
        print("❌ Tests failed!")
        print()
        print("Please fix the failing tests before proceeding.")
        
    return result.returncode


def run_specific_test_class(test_class):
    """Run a specific test class."""
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "-k", test_class,
        "--tb=short"
    ]
    
    print(f"Running specific test class: {test_class}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def run_quick_smoke_test():
    """Run a quick smoke test of critical functionality."""
    print("=" * 70)
    print("Running Quick Smoke Test")
    print("=" * 70)
    print()
    
    critical_tests = [
        "test_process_command_displays_correct_document_count",
        "test_vector_info_command_displays_collection_details",
        "test_process_command_shows_correct_next_steps",
        "test_vdq_alias_works_for_main_commands"
    ]
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "-k", " or ".join(critical_tests),
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    print()
    if result.returncode == 0:
        print("✅ Smoke test passed!")
    else:
        print("❌ Smoke test failed!")
        
    return result.returncode


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run CLI tests")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run quick smoke test only"
    )
    parser.add_argument(
        "--class",
        dest="test_class",
        help="Run specific test class"
    )
    
    args = parser.parse_args()
    
    if args.smoke:
        exit_code = run_quick_smoke_test()
    elif args.test_class:
        exit_code = run_specific_test_class(args.test_class)
    else:
        exit_code = run_tests()
        
    sys.exit(exit_code)