#!/usr/bin/env python3
"""Test runner for GPU Benchmark Tool.

This script runs all tests in the test suite and provides a summary of results.
"""

import unittest
import sys
import os
import time

# Add the parent directory to the path so we can import gpu_benchmark
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from tests.test_gpu_info import *
from tests.test_stress_tests import *
from tests.test_benchmark import *
from tests.test_cli import *
from tests.test_scoring import *
from tests.test_monitor import *
from tests.test_backends import *
from tests.test_diagnostics import *
from tests.test_utils import *


def run_all_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        # GPU Info tests
        TestGPUInfo,
        TestBackendDetection,
        TestMockBackend,
        TestMockMonitor,
        
        # Stress Tests
        TestComputeStressTest,
        TestMemoryStressTest,
        TestMixedPrecisionTest,
        
        # Benchmark tests
        TestBenchmark,
        TestBenchmarkIntegration,
        
        # CLI tests
        TestCLIOutput,
        TestCLICommands,
        TestCLIMain,
        
        # Scoring tests
        TestScoring,
        
        # Monitor tests
        TestTemperatureStability,
        TestStressGPUWithMonitoring,
        TestEnhancedStressTest,
        TestMockMonitorIntegration,
        
        # Backend tests
        TestBackendBase,
        TestMockBackend,
        TestMockMonitor,
        TestNVIDIABackend,
        TestNVIDIAMonitor,
        TestAMDBackend,
        TestAMDMonitor,
        TestIntelBackend,
        
        # Diagnostic tests
        TestEnhancedMonitoringRequirements,
        TestComprehensiveDiagnostics,
        TestDiagnosticPrintFunctions,
        
        # Utils tests
        TestColors,
        TestProgressBar,
        TestFormatting,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    return result, end_time - start_time


def main():
    """Main function to run tests."""
    print("=" * 60)
    print("GPU Benchmark Tool - Test Suite")
    print("=" * 60)
    print()
    
    # Run tests
    result, duration = run_all_tests()
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Duration: {duration:.2f} seconds")
    print()
    
    # Print failures
    if result.failures:
        print("FAILURES:")
        print("-" * 20)
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)
            print()
    
    # Print errors
    if result.errors:
        print("ERRORS:")
        print("-" * 20)
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)
            print()
    
    # Return exit code
    if result.failures or result.errors:
        print("❌ Some tests failed!")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main()) 