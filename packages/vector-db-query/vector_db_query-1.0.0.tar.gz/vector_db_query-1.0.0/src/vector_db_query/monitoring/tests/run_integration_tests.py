#!/usr/bin/env python3
"""
Integration test runner for the monitoring system.

This script runs all integration tests and generates a comprehensive report.
"""

import sys
import os
import time
import pytest
import argparse
from pathlib import Path
from datetime import datetime


def run_integration_tests(verbose=False, coverage=False, specific_test=None):
    """Run integration tests with optional coverage and reporting."""
    
    # Add the project root to the path
    project_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    print("=" * 80)
    print("MONITORING SYSTEM INTEGRATION TESTS")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {project_root}")
    print("=" * 80)
    
    # Prepare pytest arguments
    pytest_args = [
        str(Path(__file__).parent),  # Test directory
        "-v" if verbose else "-q",   # Verbosity
        "--tb=short",                 # Traceback format
        "-x",                         # Stop on first failure
        "--color=yes",                # Colored output
    ]
    
    # Add coverage if requested
    if coverage:
        pytest_args.extend([
            "--cov=vector_db_query.monitoring",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-config=.coveragerc"
        ])
    
    # Add specific test if requested
    if specific_test:
        pytest_args.append(f"-k {specific_test}")
    
    # Add custom markers
    pytest_args.extend([
        "-m", "not slow"  # Skip slow tests by default
    ])
    
    # Run tests
    start_time = time.time()
    
    try:
        exit_code = pytest.main(pytest_args)
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        if exit_code == 0:
            print("✅ ALL TESTS PASSED")
        else:
            print("❌ SOME TESTS FAILED")
        
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Exit code: {exit_code}")
        
        if coverage:
            print(f"\nCoverage report generated in: htmlcov/index.html")
        
        return exit_code
        
    except Exception as e:
        print(f"\n❌ ERROR running tests: {e}")
        return 1


def run_specific_test_suites():
    """Run specific test suites with detailed reporting."""
    
    test_suites = {
        "core": {
            "name": "Core Integration Tests",
            "pattern": "test_integration.py",
            "description": "Tests core monitoring system integration"
        },
        "dashboard": {
            "name": "Dashboard Integration Tests",
            "pattern": "test_dashboard_integration.py",
            "description": "Tests dashboard UI and widget system"
        },
        "security": {
            "name": "Security Integration Tests",
            "pattern": "test_security_integration.py",
            "description": "Tests security, API keys, and audit system"
        }
    }
    
    results = {}
    
    for suite_key, suite_info in test_suites.items():
        print(f"\n{'=' * 80}")
        print(f"Running {suite_info['name']}")
        print(f"Description: {suite_info['description']}")
        print(f"Pattern: {suite_info['pattern']}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run the specific test file
        exit_code = pytest.main([
            str(Path(__file__).parent / suite_info['pattern']),
            "-v",
            "--tb=short"
        ])
        
        elapsed_time = time.time() - start_time
        
        results[suite_key] = {
            "name": suite_info['name'],
            "exit_code": exit_code,
            "elapsed_time": elapsed_time,
            "status": "PASSED" if exit_code == 0 else "FAILED"
        }
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    
    total_time = sum(r['elapsed_time'] for r in results.values())
    failed_count = sum(1 for r in results.values() if r['exit_code'] != 0)
    
    for suite_key, result in results.items():
        status_icon = "✅" if result['exit_code'] == 0 else "❌"
        print(f"{status_icon} {result['name']}: {result['status']} ({result['elapsed_time']:.2f}s)")
    
    print(f"\nTotal time: {total_time:.2f} seconds")
    print(f"Failed suites: {failed_count}/{len(results)}")
    
    return 0 if failed_count == 0 else 1


def generate_test_report(output_file="test_report.md"):
    """Generate a detailed test report in Markdown format."""
    
    print(f"\nGenerating test report: {output_file}")
    
    # Run tests with JSON report
    import json
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_report = f.name
    
    # Run pytest with JSON output
    pytest.main([
        str(Path(__file__).parent),
        "--json-report",
        f"--json-report-file={json_report}",
        "-q"
    ])
    
    # Read JSON report
    try:
        with open(json_report, 'r') as f:
            report_data = json.load(f)
    except:
        print("Note: Install pytest-json-report for detailed JSON reports")
        report_data = None
    
    # Generate Markdown report
    with open(output_file, 'w') as f:
        f.write("# Monitoring System Integration Test Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if report_data:
            f.write("## Summary\n\n")
            f.write(f"- Total Tests: {report_data.get('summary', {}).get('total', 'N/A')}\n")
            f.write(f"- Passed: {report_data.get('summary', {}).get('passed', 'N/A')}\n")
            f.write(f"- Failed: {report_data.get('summary', {}).get('failed', 'N/A')}\n")
            f.write(f"- Duration: {report_data.get('duration', 'N/A')}s\n\n")
        
        f.write("## Test Categories\n\n")
        f.write("### Core Integration Tests\n")
        f.write("- Audit logging functionality\n")
        f.write("- Security system integration\n")
        f.write("- Change tracking integration\n")
        f.write("- Event listener integration\n")
        f.write("- Compliance reporting\n")
        f.write("- Performance under load\n\n")
        
        f.write("### Dashboard Integration Tests\n")
        f.write("- Layout management\n")
        f.write("- Widget registry\n")
        f.write("- Export functionality\n")
        f.write("- State persistence\n")
        f.write("- Concurrent operations\n\n")
        
        f.write("### Security Integration Tests\n")
        f.write("- API key lifecycle\n")
        f.write("- Permission system\n")
        f.write("- Rate limiting\n")
        f.write("- IP restrictions\n")
        f.write("- Security analytics\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. Run integration tests before deployment\n")
        f.write("2. Monitor test execution time trends\n")
        f.write("3. Maintain test coverage above 80%\n")
        f.write("4. Review failed tests immediately\n")
        f.write("5. Update tests when adding new features\n")
    
    print(f"✅ Test report generated: {output_file}")
    
    # Clean up
    if os.path.exists(json_report):
        os.remove(json_report)


def main():
    """Main entry point for the test runner."""
    
    parser = argparse.ArgumentParser(
        description="Run integration tests for the monitoring system"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "-k", "--test",
        type=str,
        help="Run specific test by name pattern"
    )
    
    parser.add_argument(
        "-s", "--suites",
        action="store_true",
        help="Run test suites individually"
    )
    
    parser.add_argument(
        "-r", "--report",
        action="store_true",
        help="Generate test report"
    )
    
    parser.add_argument(
        "--slow",
        action="store_true",
        help="Include slow tests"
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.report:
        generate_test_report()
        return 0
    
    if args.suites:
        return run_specific_test_suites()
    
    # Modify pytest args for slow tests
    if args.slow:
        os.environ['PYTEST_CURRENT_TEST'] = 'include_slow'
    
    # Run standard integration tests
    return run_integration_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        specific_test=args.test
    )


if __name__ == "__main__":
    sys.exit(main())