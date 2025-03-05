# tests/run_tests.py

import unittest
import sys
import os


def run_all_tests():
    # Set up the test loader
    loader = unittest.TestLoader()

    # Get the directory containing this script
    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Discover all tests in the test directory
    test_suite = loader.discover(start_dir=test_dir, pattern="test_*.py")

    # Create a test runner
    test_runner = unittest.TextTestRunner(verbosity=2)

    # Run the tests
    result = test_runner.run(test_suite)

    # Return appropriate exit code (0 for success, 1 for failure)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
