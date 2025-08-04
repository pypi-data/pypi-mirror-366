#!/usr/bin/env python3
"""Run all format integration tests with coverage report."""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all integration tests for extended format support."""
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Test files to run
    test_files = [
        "test_all_formats_integration.py",
        "test_reader_edge_cases.py", 
        "test_cli_format_integration.py",
        # Also run existing related tests
        "test_config_reader.py",
        "test_excel_reader.py",
        "test_html_reader.py",
        "test_email_reader.py",
        "test_powerpoint_reader.py",
        "test_ocr_reader.py",
        "test_config_enhanced.py",
        "test_process_enhanced_direct.py",
    ]
    
    print("🧪 Running Extended Format Support Integration Tests")
    print("=" * 60)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        "--cov=src.vector_db_query.document_processor",
        "--cov=src.vector_db_query.cli.commands",
        "--cov=src.vector_db_query.utils.config_enhanced",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
    ]
    
    # Add test files
    for test_file in test_files:
        test_path = test_dir / test_file
        if test_path.exists():
            cmd.append(str(test_path))
        else:
            print(f"⚠️  Warning: {test_file} not found")
    
    # Add markers for specific test types
    cmd.extend([
        "-m", "not slow",  # Skip slow tests by default
        "--maxfail=5",     # Stop after 5 failures
    ])
    
    print(f"\n📍 Running command: {' '.join(cmd)}\n")
    
    # Run tests
    result = subprocess.run(cmd, cwd=str(project_root))
    
    if result.returncode == 0:
        print("\n✅ All integration tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with exit code: {result.returncode}")
    
    return result.returncode


def run_specific_category(category):
    """Run tests for a specific category."""
    categories = {
        "formats": ["test_all_formats_integration.py"],
        "edge": ["test_reader_edge_cases.py"],
        "cli": ["test_cli_format_integration.py"],
        "readers": [
            "test_config_reader.py",
            "test_excel_reader.py",
            "test_html_reader.py",
            "test_email_reader.py",
            "test_powerpoint_reader.py",
            "test_ocr_reader.py",
        ],
        "config": ["test_config_enhanced.py"],
    }
    
    if category not in categories:
        print(f"❌ Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return 1
    
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
    ]
    
    for test_file in categories[category]:
        test_path = test_dir / test_file
        if test_path.exists():
            cmd.append(str(test_path))
    
    print(f"\n🧪 Running {category} tests...")
    result = subprocess.run(cmd, cwd=str(project_root))
    
    return result.returncode


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific category
        category = sys.argv[1]
        return run_specific_category(category)
    else:
        # Run all tests
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())