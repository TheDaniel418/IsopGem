#!/usr/bin/env python
"""Run tests in a clean way without warnings and coverage.

This script runs the tests in a more user-friendly way, focusing just
on test success/failure without all the warnings and coverage details.
"""

import os
import sys
import subprocess


def run_tests(specific_test=None):
    """Run tests with warnings disabled and no coverage check.
    
    Args:
        specific_test: Optional path to a specific test file/directory
    """
    cmd = [
        sys.executable, 
        "-m", 
        "pytest",
        "--disable-warnings",  # Disable warnings
        "-v",                  # Verbose output
        "--no-header",         # Hide pytest header
        "--no-summary",        # Hide pytest summary
    ]
    
    # Add specific test path if provided
    if specific_test:
        cmd.append(specific_test)
    
    # Run the command
    print(f"\n🧪 Running tests: {' '.join(cmd[2:])}\n")
    result = subprocess.run(cmd)
    
    # Print summary
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    # Return the exit code
    return result.returncode


if __name__ == "__main__":
    # Get specific test path from command line if provided
    specific_test = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the tests
    exit_code = run_tests(specific_test)
    
    # Exit with the test result
    sys.exit(exit_code) 