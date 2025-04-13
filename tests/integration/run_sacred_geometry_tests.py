#!/usr/bin/env python3
"""Run integration tests for the Sacred Geometry Explorer.

This script runs the integration tests for the Sacred Geometry Explorer.
"""

import os
import sys
import unittest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the test module
from tests.integration.test_sacred_geometry_integration import TestSacredGeometryIntegration

if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSacredGeometryIntegration)
    
    # Run the tests
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())
