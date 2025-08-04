#!/usr/bin/env python3
"""Test the enhanced CLI commands."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Run a CLI command and return output."""
    result = subprocess.run(
        [sys.executable, "-m", "vector_db_query"] + cmd.split(),
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def test_formats_flag():
    """Test the --formats flag."""
    print("\n=== Testing --formats flag ===")
    code, stdout, stderr = run_command("process --formats")
    print(f"Exit code: {code}")
    print(f"Output:\n{stdout}")
    if stderr:
        print(f"Errors:\n{stderr}")

def test_detect_format():
    """Test the detect-format command."""
    print("\n=== Testing detect-format command ===")
    
    # Test on a specific file
    test_file = Path(__file__)
    code, stdout, stderr = run_command(f"detect-format {test_file}")
    print(f"Exit code: {code}")
    print(f"Output:\n{stdout}")
    if stderr:
        print(f"Errors:\n{stderr}")
    
    # Test on a directory
    test_dir = test_file.parent
    code, stdout, stderr = run_command(f"detect-format {test_dir} --detailed")
    print(f"\nDetailed directory scan:")
    print(f"Exit code: {code}")
    print(f"Output:\n{stdout}")

def test_extension_filter():
    """Test extension filtering."""
    print("\n=== Testing extension filtering ===")
    
    # Dry run with extension filter
    test_dir = Path(__file__).parent
    code, stdout, stderr = run_command(f"process --folder {test_dir} --extensions .py --extensions .txt --dry-run")
    print(f"Exit code: {code}")
    print(f"Output:\n{stdout}")

def test_help():
    """Test help text for new options."""
    print("\n=== Testing help text ===")
    code, stdout, stderr = run_command("process --help")
    print("Process command help:")
    print(stdout)
    
    print("\n" + "="*50 + "\n")
    
    code, stdout, stderr = run_command("detect-format --help")
    print("Detect-format command help:")
    print(stdout)

if __name__ == "__main__":
    print("Testing Enhanced CLI Features")
    print("="*50)
    
    test_help()
    test_formats_flag()
    test_detect_format()
    test_extension_filter()
    
    print("\n\nAll tests completed!")