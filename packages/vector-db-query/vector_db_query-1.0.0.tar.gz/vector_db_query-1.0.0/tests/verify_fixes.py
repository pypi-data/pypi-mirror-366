#!/usr/bin/env python3
"""Quick verification script for CLI fixes.

This script performs basic checks to verify the fixes are in place.
"""

import sys
from pathlib import Path
import ast


def check_vectors_stored_fix():
    """Check if vectors_stored fix is in place."""
    print("Checking vectors_stored fix in process_fixed.py...")
    
    process_file = Path(__file__).parent.parent / "src/vector_db_query/cli/commands/process_fixed.py"
    
    if not process_file.exists():
        print("❌ process_fixed.py not found!")
        return False
        
    content = process_file.read_text()
    
    # Check line 182 contains vectors_stored
    lines = content.split('\n')
    if len(lines) > 181:
        line_182 = lines[181]  # 0-indexed
        if 'vectors_stored' in line_182 and 'result.get' in line_182:
            print("✅ Line 182 correctly uses 'vectors_stored'")
            return True
        else:
            print(f"❌ Line 182 does not contain expected fix: {line_182}")
            return False
    else:
        print("❌ File has less than 182 lines")
        return False


def check_vector_info_command():
    """Check if vector info command exists."""
    print("\nChecking vector info command in vector.py...")
    
    vector_file = Path(__file__).parent.parent / "src/vector_db_query/cli/commands/vector.py"
    
    if not vector_file.exists():
        print("❌ vector.py not found!")
        return False
        
    content = vector_file.read_text()
    
    # Check for info command definition
    if "@vector.command(name='info')" in content or "@vector.command('info')" in content:
        print("✅ Vector info command is defined")
        
        # Check for proper function
        if "def info(collection_name: str):" in content:
            print("✅ Info function has correct signature")
            return True
        else:
            print("⚠️  Info function signature might be different")
            return True
    else:
        print("❌ Vector info command not found")
        return False


def check_command_suggestions():
    """Check if command suggestions are correct."""
    print("\nChecking command suggestions in process_fixed.py...")
    
    process_file = Path(__file__).parent.parent / "src/vector_db_query/cli/commands/process_fixed.py"
    content = process_file.read_text()
    
    # Check for correct suggestions
    suggestions = [
        "vdq query 'your search query'",
        "vdq interactive",
        "vector-db-query vector info"
    ]
    
    found_all = True
    for suggestion in suggestions:
        if suggestion in content:
            print(f"✅ Found correct suggestion: {suggestion}")
        else:
            print(f"❌ Missing suggestion: {suggestion}")
            found_all = False
            
    return found_all


def check_vdq_alias():
    """Check if vdq alias is configured."""
    print("\nChecking vdq alias in pyproject.toml...")
    
    pyproject_file = Path(__file__).parent.parent / "pyproject.toml"
    
    if not pyproject_file.exists():
        print("❌ pyproject.toml not found!")
        return False
        
    content = pyproject_file.read_text()
    
    # Check for vdq entry in scripts
    if 'vdq = "vector_db_query.__main__:main"' in content:
        print("✅ VDQ alias is properly configured")
        return True
    else:
        print("❌ VDQ alias not found in pyproject.toml")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Verifying CLI Display Storage Fixes")
    print("=" * 60)
    
    checks = [
        check_vectors_stored_fix(),
        check_vector_info_command(),
        check_command_suggestions(),
        check_vdq_alias()
    ]
    
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        return 0
    else:
        print(f"❌ Some checks failed! ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())