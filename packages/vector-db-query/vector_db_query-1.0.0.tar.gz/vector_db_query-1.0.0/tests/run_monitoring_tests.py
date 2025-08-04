#!/usr/bin/env python3
"""
Test runner for Ansera monitoring system unit tests.

This script runs all unit tests for the monitoring components
and provides a summary of the results.
"""

import sys
import unittest
import os
from pathlib import Path

# Add parent directory to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from tests.test_monitoring_metrics import TestSystemMonitor, TestSystemMetrics
from tests.test_monitoring_process_manager import TestProcessingJob, TestQueueMonitor, TestQueueMetrics
from tests.test_monitoring_controls import TestProcessController, TestGetController
from tests.test_monitoring_pm2_control import TestPM2Controller, TestGetPM2Controller


def run_all_tests():
    """Run all monitoring unit tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        # Metrics tests
        TestSystemMonitor,
        TestSystemMetrics,
        
        # Process manager tests
        TestProcessingJob,
        TestQueueMonitor,
        TestQueueMetrics,
        
        # Controls tests
        TestProcessController,
        TestGetController,
        
        # PM2 control tests
        TestPM2Controller,
        TestGetPM2Controller
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("MONITORING SYSTEM TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


def run_specific_module(module_name):
    """Run tests for a specific module."""
    module_map = {
        'metrics': [TestSystemMonitor, TestSystemMetrics],
        'process_manager': [TestProcessingJob, TestQueueMonitor, TestQueueMetrics],
        'controls': [TestProcessController, TestGetController],
        'pm2': [TestPM2Controller, TestGetPM2Controller]
    }
    
    if module_name not in module_map:
        print(f"Unknown module: {module_name}")
        print(f"Available modules: {', '.join(module_map.keys())}")
        return 1
    
    # Create test suite for specific module
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_class in module_map[module_name]:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n{module_name.upper()} MODULE TEST RESULTS:")
    print(f"Tests run: {result.testsRun}")
    print(f"Success: {result.wasSuccessful()}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific module tests
        exit_code = run_specific_module(sys.argv[1])
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)