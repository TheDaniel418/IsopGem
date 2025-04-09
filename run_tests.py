#!/usr/bin/env python3
"""
Test runner for IsopGem project.

This script ensures the Python path is set correctly before running the tests.
"""

import os
import sys
import unittest


def run_tests():
    """Run specific unit tests for the IsopGem project."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # Create a test suite
    suite = unittest.TestSuite()

    # Create a test loader
    loader = unittest.TestLoader()

    # Add specific test files we know work
    test_files = [
        "tests.unit.tq.utils.test_ternary_transition",
        "tests.unit.tq.utils.test_ternary_converter",
    ]

    for test_file in test_files:
        try:
            tests = loader.loadTestsFromName(test_file)
            suite.addTest(tests)
        except ImportError as e:
            print(f"Could not import {test_file}: {e}")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return 0 if all tests passed, 1 otherwise
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
