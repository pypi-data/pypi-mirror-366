#!/usr/bin/env python3
"""Test CLI command structure without full imports."""

import subprocess
import sys
from pathlib import Path

def test_cli_help():
    """Test basic CLI help."""
    print("\n=== Testing basic CLI help ===")
    result = subprocess.run(
        [sys.executable, "-m", "vector_db_query", "--help"],
        capture_output=True,
        text=True
    )
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("✓ CLI loads successfully")
        print("\nAvailable commands:")
        # Extract commands from help text
        for line in result.stdout.split('\n'):
            if line.strip().startswith('detect-format') or line.strip().startswith('process'):
                print(f"  - {line.strip()}")
    else:
        print("✗ CLI failed to load")
        print(f"Error: {result.stderr}")

def test_command_exists():
    """Check if our new commands are registered."""
    print("\n=== Checking command registration ===")
    
    # Test if process command has new options
    result = subprocess.run(
        [sys.executable, "-c", 
         "from vector_db_query.cli.main import cli; "
         "process_cmd = cli.commands.get('process'); "
         "if process_cmd: "
         "    print('Process command found'); "
         "    params = [p.name for p in process_cmd.params]; "
         "    if 'formats' in params: print('  ✓ --formats option found'); "
         "    if 'extensions' in params: print('  ✓ --extensions option found'); "
         "    if 'ocr_lang' in params: print('  ✓ --ocr-lang option found'); "
         "detect_cmd = cli.commands.get('detect-format'); "
         "if detect_cmd: print('✓ detect-format command found')"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

def test_module_imports():
    """Test if enhanced modules can be imported."""
    print("\n=== Testing module imports ===")
    
    try:
        # Test process_enhanced import
        result = subprocess.run(
            [sys.executable, "-c", 
             "from vector_db_query.cli.commands.process_enhanced import process_command, detect_format; "
             "print('✓ process_enhanced module imports successfully')"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Import error: {result.stderr}")
            
        # Test reader factory
        result = subprocess.run(
            [sys.executable, "-c", 
             "from vector_db_query.document_processor.reader import ReaderFactory; "
             "factory = ReaderFactory(); "
             "print(f'✓ ReaderFactory loaded with {len(factory.supported_extensions)} extensions')"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
    except Exception as e:
        print(f"✗ Import failed: {e}")

if __name__ == "__main__":
    print("Testing CLI Command Structure")
    print("="*50)
    
    test_module_imports()
    test_cli_help()
    test_command_exists()
    
    print("\n\nTest completed!")